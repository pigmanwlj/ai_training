#!/bin/sh
set -eu

PROFILE="rtx5090"
HOST_ALIAS="ollama_rtx5090"

RAW_USER="${1:-${SUDO_USER:-${USER:-anon}}}"
SAFE_USER="$(printf '%s' "$RAW_USER" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_.-')"
if [ -z "$SAFE_USER" ]; then
  SAFE_USER="anon"
fi

TS="$(date +%s)"
RAND="$(od -An -N3 -tx1 /dev/urandom | tr -d ' \n')"
if [ -z "$RAND" ]; then
  RAND="$TS"
fi

BASE_NAME="ollama-${PROFILE}-${SAFE_USER}-${TS}-${RAND}"
CONTAINER_NAME="$(printf '%s' "$BASE_NAME" | cut -c1-63)"

while docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; do
  RAND="$(od -An -N3 -tx1 /dev/urandom | tr -d ' \n')"
  if [ -z "$RAND" ]; then
    RAND="$(date +%s)"
  fi
  BASE_NAME="ollama-${PROFILE}-${SAFE_USER}-${TS}-${RAND}"
  CONTAINER_NAME="$(printf '%s' "$BASE_NAME" | cut -c1-63)"
done

docker run -d \
  --name "$CONTAINER_NAME" \
  --hostname "$HOST_ALIAS" \
  --link ollamarepo:airepository.saicmotor.com \
  --label training.owner="$SAFE_USER" \
  --label training.profile="$PROFILE" \
  -v /data/ollama/training:/root/.ollama \
  -p 0:11434 \
  ollama/ollama >/dev/null

HOST_PORT="$(docker port "$CONTAINER_NAME" 11434/tcp | awk -F: 'NR==1{print $2}')"
if [ -z "$HOST_PORT" ]; then
  echo "ERROR=Unable to resolve mapped host port"
  exit 1
fi

echo "CONTAINER_NAME=$CONTAINER_NAME"
echo "HOST_PORT=$HOST_PORT"
echo "PROFILE=$PROFILE"
echo "OWNER=$SAFE_USER"

