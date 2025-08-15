#!/usr/bin/env bash
set -e
HOST=${1:-127.0.0.1}
USER=${2:-your_mqtt_username}
PASS=${3:-your_mqtt_password}
SUBTOPIC=${4:-'msh/#'}
PUBTOPIC=${5:-'msh/US/2/json/test'}
MSG='{"ping":"selftest"}'

echo "[*] Installing mosquitto-clients if missing..."
if ! command -v mosquitto_sub >/dev/null 2>&1; then
  sudo apt update && sudo apt install -y mosquitto-clients
fi

echo "[*] Starting subscriber on $HOST topic=$SUBTOPIC"
mosquitto_sub -d -h "$HOST" -p 1883 -u "$USER" -P "$PASS" -t "$SUBTOPIC" -v > /tmp/mqtt_sub.out 2>&1 &
SUB_PID=$!
sleep 1

echo "[*] Publishing test message to $PUBTOPIC"
mosquitto_pub -d -h "$HOST" -p 1883 -u "$USER" -P "$PASS" -t "$PUBTOPIC" -m "$MSG"

sleep 1
kill $SUB_PID || true

echo "[*] Subscriber output:"
cat /tmp/mqtt_sub.out || true


