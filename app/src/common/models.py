from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    Column,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, DOUBLE_PRECISION
from sqlalchemy.orm import relationship, Mapped, mapped_column

from common.db import Base


class User(Base):
    __tablename__ = "users"

    tg_user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    tg_chat_id = Column(BigInteger, nullable=True)
    language = Column(String(2), nullable=False, server_default="en")
    tg_code = Column(String(8), unique=True, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    # relationships
    nodes = relationship("Node", back_populates="owner", lazy="selectin")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, unique=True, nullable=False)
    alias = Column(String(64), nullable=True)
    user_label: Mapped[str | None] = mapped_column(default=None)
    owner_tg_user_id = Column(BigInteger, ForeignKey("users.tg_user_id"), nullable=True)
    last_seen_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_gateway_node_id = Column(BigInteger, nullable=True)

    # Position info
    last_lat = Column(DOUBLE_PRECISION, nullable=True)
    last_lon = Column(DOUBLE_PRECISION, nullable=True)
    last_alt = Column(DOUBLE_PRECISION, nullable=True)
    last_position_at = Column(TIMESTAMP(timezone=True), nullable=True)

    owner = relationship("User", back_populates="nodes", lazy="selectin")


class Gateway(Base):
    __tablename__ = "gateways"

    node_id = Column(BigInteger, primary_key=True, autoincrement=False)
    alias = Column(String(64), nullable=True)
    region = Column(String(8), nullable=False, server_default="US")
    last_seen_at = Column(TIMESTAMP(timezone=True), nullable=True)


class HeardMap(Base):
    __tablename__ = "heard_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, nullable=False)
    gateway_node_id = Column(BigInteger, nullable=False)
    last_heard_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("node_id", "gateway_node_id", name="uq_heard_map_pair"),)


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    direction = Column(String(8), nullable=False)
    msg_id = Column(String(64), nullable=True)
    from_id = Column(String(32), nullable=True)
    to_id = Column(String(32), nullable=True)
    gateway_node_id = Column(BigInteger, nullable=True)
    payload = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    __table_args__ = (UniqueConstraint("direction", "msg_id", name="uq_direction_msg_id"),)


__all__ = [
    "User",
    "Node",
    "Gateway",
    "HeardMap",
    "Message",
]


