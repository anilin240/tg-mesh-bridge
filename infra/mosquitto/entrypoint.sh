#!/usr/bin/env sh
set -e

# Env with defaults
: "${MQTT_USER:=bridge}"
: "${MQTT_PASS:=bridge}"

PASS_FILE="/mosquitto/config/passwords"
ACL_FILE="/mosquitto/config/acl"

# Ensure password file exists and is hashed for MQTT_USER
if [ ! -s "$PASS_FILE" ]; then
    # create with hashed password for the user
    mosquitto_passwd -b -c "$PASS_FILE" "$MQTT_USER" "$MQTT_PASS"
else
    # if entry for user exists and is not hashed, re-hash it
    if grep -q "^${MQTT_USER}:" "$PASS_FILE"; then
        if ! grep -q "^${MQTT_USER}:.\{1,\}\$" /dev/null 2>/dev/null; then :; fi
        # check if hashed marker ($) present after colon
        if ! awk -F: -v u="$MQTT_USER" '$1==u{if(index($2,"$")==0) exit 1; else exit 0} END{if(NR==0) exit 0}' "$PASS_FILE"; then
            mosquitto_passwd -b "$PASS_FILE" "$MQTT_USER" "$MQTT_PASS"
        fi
    else
        # add user with hashed password
        mosquitto_passwd -b "$PASS_FILE" "$MQTT_USER" "$MQTT_PASS"
    fi
fi

# Create default ACL if missing (authenticated users get R/W to msh/#). If present, keep as-is.
if [ ! -s "$ACL_FILE" ]; then
    printf "topic readwrite msh/#\n" > "$ACL_FILE"
fi

# Fix permissions so mosquitto can read them
chmod 0600 "$PASS_FILE" || true
chmod 0600 "$ACL_FILE" || true
chown mosquitto:mosquitto "$PASS_FILE" "$ACL_FILE" || true

exec mosquitto -c /mosquitto/config/mosquitto.conf


