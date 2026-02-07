#!/usr/bin/env bash
set -e

RUNTIME_NAME="sdv-runtime"
DATABROKER_NAME="kuksa-server"

VSS_DIR="/home/hhn-sdv-demo/sdvDemonstrator/kuksa_databrocker"
VSS_FILE_RUNTIME="/vss/hhn_sdv_vss.json"
VSS_FILE_STANDALONE="/vss/hhn_sdv_vss.json"

RUNTIME_IMAGE="ghcr.io/eclipse-autowrx/sdv-runtime:latest"
DATABROKER_IMAGE="ghcr.io/eclipse-kuksa/kuksa-databroker:main"

is_running() {
  docker ps --format '{{.Names}}' | grep -qx "$1"
}

exists() {
  docker ps -a --format '{{.Names}}' | grep -qx "$1"
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
    docker update --restart=always "$DATABROKER_NAME" >/dev/null 2>&1 || true
    docker start "$DATABROKER_NAME" >/dev/null
  else
    docker run -d --name "$DATABROKER_NAME" --restart always --network host \
      -v "$VSS_DIR:/vss" \
      "$DATABROKER_IMAGE" --insecure --vss "$VSS_FILE_STANDALONE" >/dev/null
  fi
}

stop_runtime() {
  docker stop "$RUNTIME_NAME" >/dev/null 2>&1 || true
}

stop_databroker() {
  docker stop "$DATABROKER_NAME" >/dev/null 2>&1 || true
}

MODE="${1:-toggle}"

if [ "$MODE" = "runtime" ]; then
  echo "Stoppe Standalone Databroker, starte Runtime"
  stop_databroker
  start_runtime
  echo "Runtime läuft"
  exit 0
fi

if [ "$MODE" = "databroker" ]; then
  echo "Stoppe Runtime, starte Standalone Databroker"
  stop_runtime
  start_databroker
  echo "Standalone Databroker läuft"
  exit 0
fi

if is_running "$RUNTIME_NAME"; then
  echo "Runtime läuft, wechsle zu Standalone Databroker"
  stop_runtime
  start_databroker
  echo "Standalone Databroker läuft"
else
  echo "Standalone Databroker läuft nicht, wechsle zu Runtime"
  stop_databroker
  start_runtime
  echo "Runtime läuft"
fi
