#!/usr/bin/env bashio
set +u

WAIT_PIDS=()

bashio::log.info "Start ble2mqtt daemon"

python3 run.py&
WAIT_PIDS+=($!)

function stop_ble2mqtt() {
    bashio::log.info "Shutdown ble2mqtt system"
    kill -15 "${WAIT_PIDS[@]}"

    wait "${WAIT_PIDS[@]}"
}
trap "stop_ble2mqtt" SIGTERM SIGHUP

wait "${WAIT_PIDS[@]}"
bashio::log.info "Ble2mqtt daemon is stopped"