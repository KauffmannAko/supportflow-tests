#!/bin/sh
set -eu

mode=${1:-test}
case "$mode" in
    up|test) ;;
    *) echo "Usage: $0 [up|test]" >&2; exit 2 ;;
esac

# Use the same Compose project as make clean (including COMPOSE_PROJECT_NAME).
compose() {
    docker compose "$@"
}
report_failure() {
    status=$?
    trap - EXIT HUP INT TERM
    if [ "$status" -ne 0 ] && [ "$resources_started" -eq 1 ]; then
        compose ps -a >&2 || :
        compose logs --no-color --tail=100 db api >&2 || :
    fi
    exit "$status"
}
resources_started=0
trap report_failure EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

compose config --quiet
compose pull api db
compose build api-tests
resources_started=1
compose up -d --wait --wait-timeout 120 db
# Published image: WORKDIR /app; no ENTRYPOINT; manage.py exists there.
compose run --rm --no-deps -T api python manage.py migrate --noinput
compose up -d --no-deps --wait --wait-timeout 120 api
if [ "$mode" = test ]; then
    compose run --rm --no-deps -T api-tests
fi
