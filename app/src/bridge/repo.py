from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from common.db import SessionLocal
from common.models import User, Node, Gateway, HeardMap, Message


def get_user_tg_id_by_code(code: str) -> Optional[int]:
    with SessionLocal() as session:
        result = session.execute(select(User.tg_user_id).where(User.tg_code == code)).scalar_one_or_none()
        return int(result) if result is not None else None


def get_user_chat_id_by_code(code: str) -> Optional[int]:
    with SessionLocal() as session:
        result = session.execute(select(User.tg_chat_id).where(User.tg_code == code)).scalar_one_or_none()
        return int(result) if result is not None else None


def upsert_node(node_id: int, last_gateway_node_id: Optional[int]) -> None:
    if node_id is None:
        return
    with SessionLocal() as session:
        stmt = (
            insert(Node.__table__)
            .values(node_id=node_id, last_seen_at=func.now(), last_gateway_node_id=last_gateway_node_id)
            .on_conflict_do_update(
                index_elements=[Node.__table__.c.node_id],
                set_={
                    "last_seen_at": func.now(),
                    "last_gateway_node_id": last_gateway_node_id,
                },
            )
        )
        session.execute(stmt)
        session.commit()


def upsert_gateway(node_id: int) -> None:
    if node_id is None:
        return
    with SessionLocal() as session:
        stmt = (
            insert(Gateway.__table__).values(node_id=node_id, last_seen_at=func.now())
            .on_conflict_do_update(
                index_elements=[Gateway.__table__.c.node_id],
                set_={"last_seen_at": func.now()},
            )
        )
        session.execute(stmt)
        session.commit()


def upsert_heard_map(node_id: int, gateway_node_id: int) -> None:
    if node_id is None or gateway_node_id is None:
        return
    with SessionLocal() as session:
        stmt = (
            insert(HeardMap.__table__)
            .values(node_id=node_id, gateway_node_id=gateway_node_id, last_heard_at=func.now())
            .on_conflict_do_update(
                index_elements=[HeardMap.__table__.c.node_id, HeardMap.__table__.c.gateway_node_id],
                set_={"last_heard_at": func.now()},
            )
        )
        session.execute(stmt)
        session.commit()


def message_exists(direction: str, msg_id: Optional[str]) -> bool:
    if not msg_id:
        return False
    with SessionLocal() as session:
        exists = session.execute(
            select(Message.id).where(Message.direction == direction, Message.msg_id == str(msg_id))
        ).first()
        return exists is not None


def save_message(
    *,
    direction: str,
    msg_id: Optional[str],
    from_id: Optional[str],
    to_id: Optional[str],
    gateway_node_id: Optional[int],
    payload: Optional[str],
) -> None:
    with SessionLocal() as session:
        # If msg_id is provided, rely on DB unique constraint to avoid dup inserts
        message = Message(
            direction=direction,
            msg_id=msg_id,
            from_id=from_id,
            to_id=to_id,
            gateway_node_id=gateway_node_id,
            payload=payload,
        )
        session.add(message)
        session.commit()


def link_node_to_user(node_id: int, tg_user_id: int) -> bool:
    """Link node to a user if not linked yet.

    Returns True if a new link was created (owner_tg_user_id was NULL or row created), False otherwise.
    """
    with SessionLocal() as session:
        node = session.execute(select(Node).where(Node.node_id == node_id)).scalar_one_or_none()
        if node is None:
            node = Node(node_id=node_id, owner_tg_user_id=tg_user_id)
            session.add(node)
            session.commit()
            return True
        if node.owner_tg_user_id is None:
            node.owner_tg_user_id = tg_user_id
            session.commit()
            return True
        return False


def update_node_alias(node_id: int, alias: str) -> None:
    if not alias:
        return
    with SessionLocal() as session:
        # ensure alias uniqueness globally
        existing = session.execute(select(Node).where(Node.alias == alias)).scalar_one_or_none()
        if existing and existing.node_id != node_id:
            # do not overwrite if taken
            return
        node = session.execute(select(Node).where(Node.node_id == node_id)).scalar_one_or_none()
        if node is None:
            node = Node(node_id=node_id, alias=alias)
            session.add(node)
        else:
            node.alias = alias
        session.commit()


def update_node_position(node_id: int, lat: float, lon: float, alt: Optional[float], at) -> None:
    with SessionLocal() as session:
        node = session.execute(select(Node).where(Node.node_id == node_id)).scalar_one_or_none()
        if node is None:
            node = Node(node_id=node_id)
            session.add(node)
        node.last_lat = float(lat) if lat is not None else None
        node.last_lon = float(lon) if lon is not None else None
        node.last_alt = float(alt) if alt is not None else None
        node.last_position_at = at
        session.commit()


def get_user_devices(tg_user_id: int):
    with SessionLocal() as s:
        return list(s.scalars(select(Node).where(Node.owner_tg_user_id == tg_user_id)).all())


def get_device_by_id_for_user(node_id: int, tg_user_id: int):
    with SessionLocal() as s:
        return s.scalar(select(Node).where(Node.node_id == node_id, Node.owner_tg_user_id == tg_user_id))


def link_node_to_user_manual(node_id: int, tg_user_id: int) -> str:
    with SessionLocal() as s:
        n = s.scalar(select(Node).where(Node.node_id == node_id))
        cnt = s.scalar(select(func.count()).select_from(Node).where(Node.owner_tg_user_id == tg_user_id)) or 0
        if cnt >= 3:
            return "limit"
        if n:
            if n.owner_tg_user_id == tg_user_id:
                return "already"
            if n.owner_tg_user_id and n.owner_tg_user_id != tg_user_id:
                return "owned_by_other"
            n.owner_tg_user_id = tg_user_id
            s.commit()
            return "ok"
        n = Node(node_id=node_id, owner_tg_user_id=tg_user_id)
        s.add(n); s.commit()
        return "ok"


def rename_user_device(node_id: int, tg_user_id: int, label: str) -> bool:
    with SessionLocal() as s:
        n = s.scalar(select(Node).where(Node.node_id == node_id, Node.owner_tg_user_id == tg_user_id))
        if not n:
            return False
        n.user_label = label
        s.commit()
        return True


def delete_user_device(node_id: int, tg_user_id: int) -> bool:
    with SessionLocal() as s:
        n = s.scalar(select(Node).where(Node.node_id == node_id, Node.owner_tg_user_id == tg_user_id))
        if not n:
            return False
        n.owner_tg_user_id = None
        s.commit()
        return True


