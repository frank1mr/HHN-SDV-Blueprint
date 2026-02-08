#!/usr/bin/env bash
set -e

# Container Namen
RUNTIME_NAME="sdv-runtime"
DATABROKER_NAME="kuksa-server"

# Feeder und Bridge Container Namen (anpassen)
FEEDERS=("dbc-feeder-front" "dbc-feeder-rear")
BRIDGES=("can-udp-bridge")

# VSS Setup
VSS_DIR="/home/hhn-sdv-demo/sdvDemonstrator/kuksa_databrocker"
VSS_FILE_RUNTIME="/vss/hhn_sdv_vss.json"
VSS_FILE_STANDALONE="/vss/hhn_sdv_vss.json"

# Images
RUNTIME_IMAGE="ghcr.io/eclipse-autowrx/sdv-runtime:latest"
DATABROKER_IMAGE="ghcr.io/eclipse-kuksa/kuksa-databroker:main"

exists() { docker ps -a --format '{{.Names}}' | grep -qx "$1"; }
is_running() { docker ps --format '{{.Names}}' | grep -qx "$1"; }

stop_container() {
  docker stop "$1" >/dev/null 2>&1 || true
}

start_runtime() {
  if exists "$RUNTIME_NAME"; then
    docker update --restart=always "$RUNTIME_NAME" >/dev/null 2>&1 || true
    docker start "$RUNTIME_NAME" >/dev/null
  else
    docker run -d --name "$RUNTIME_NAME" --restart always --network host \
      -e RUNTIME_NAME="sdv-runtime" \
      -e KUKSA_DATABROKER_METADATA_FILE="$VSS_FILE_RUNTIME" \
      -v "$VSS_DIR:/vss" \
      "$RUNTIME_IMAGE" >/dev/null
  fi
}

start_databroker() {
  if exists "$DATABROKER_NAME"; then
    docker start "$DATABROKER_NAME" >/dev/null
  else
    docker run -d --name "$DATABROKER_NAME" --restart always --network host \
      -v "$VSS_DIR:/vss" \
      "$DATABROKER_IMAGE" --insecure --vss "$VSS_FILE_STANDALONE" >/dev/null
  fi
}

restart_if_exists() {
  local name="$1"
  if exists "$name"; then
    docker restart "$name" >/dev/null || true
  fi
}

restart_infra() {
  for c in "${BRIDGES[@]}"; do restart_if_exists "$c"; done
  for c in "${FEEDERS[@]}"; do restart_if_exists "$c"; done
}

switch_to_runtime() {
  stop_container "$DATABROKER_NAME"
  sleep 10
  start_runtime
  sleep 2
  restart_infra
}

switch_to_databroker() {
  stop_container "$RUNTIME_NAME"
  sleep 10
  start_databroker
  sleep 2
  restart_infra
}

MODE="${1:-toggle}"

if [ "$MODE" = "runtime" ]; then
  switch_to_runtime
  exit 0
fi

if [ "$MODE" = "databroker" ]; then
  switch_to_databroker
  exit 0
fi

if is_running "$RUNTIME_NAME"; then
  switch_to_databroker
else
  switch_to_runtime
fi
