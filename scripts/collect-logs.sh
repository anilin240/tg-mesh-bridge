#!/usr/bin/env bash
set -e
TS=$(date +%F_%H%M%S)
OUT=~/tg-mesh-logs-$TS
mkdir -p "$OUT"
cd ~/your_project_path/infra

docker compose ps > "$OUT/compose-ps.txt"
docker compose config > "$OUT/compose-config.yaml"
docker compose logs --no-color > "$OUT/stack.log"
docker compose logs --no-color app > "$OUT/app.log"
docker compose logs --no-color mosquitto > "$OUT/mosquitto.log"
docker compose logs --no-color postgres > "$OUT/postgres.log"

docker compose exec mosquitto sh -lc 'cat /mosquitto/config/mosquitto.conf' > "$OUT/mosquitto.conf"
docker compose exec mosquitto sh -lc 'cat /mosquitto/config/acl' > "$OUT/mosquitto.acl"

cd ~
zip -r "tg-mesh-logs-$TS.zip" "tg-mesh-logs-$TS"
echo "[*] Logs packed at ~/tg-mesh-logs-$TS.zip"


