#!/usr/bin/env bash
set -euo pipefail
HOST=${1:-127.0.0.1}; PORT=${2:-1883}; USER=${3:-bridge}; PASS=${4:-bridge}
echo "[*] Checking port ${PORT} ..."
sudo ss -lntp | grep ":${PORT}" || echo "No listener on ${PORT}"
echo "[*] Broker logs (docker) ..."
( cd infra && docker compose logs mosquitto --since=2m || true )
echo "[*] Subscribing..."
mosquitto_sub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" -t 'msh/#' -v > /tmp/mqtt_doctor.out 2>&1 &
PID=$!; sleep 1
MSG="{\"ping\":\"doctor\",\"ts\":$(date +%s)}"
echo "[*] Publishing test..."
mosquitto_pub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" -t 'msh/US/2/json/test' -m "$MSG" || true
sleep 1; kill $PID || true
echo "[*] Subscriber output:"; cat /tmp/mqtt_doctor.out || true


