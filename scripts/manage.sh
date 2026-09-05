#!/usr/bin/env bash
# ==============================================================================
# AlamiaTravelOS - Linux/VPS Management Helper Script
# ==============================================================================

set -e

COMMAND=$1
ARG1=$2

case "$COMMAND" in
    up)
        echo "Starting AlamiaTravelOS containers..."
        docker compose up -d
        echo "Odoo 19 is running."
        ;;
    up:prod)
        echo "Starting AlamiaTravelOS Production stack..."
        docker compose -f docker-compose.prod.yml up -d
        ;;
    down)
        echo "Stopping containers..."
        docker compose down
        ;;
    down:prod)
        echo "Stopping production stack..."
        docker compose -f docker-compose.prod.yml down
        ;;
    restart)
        echo "Restarting Odoo container..."
        docker compose restart web
        ;;
    logs)
        docker compose logs -f "${ARG1:-web}"
        ;;
    ps)
        docker compose ps
        ;;
    shell)
        docker compose exec -it web bash
        ;;
    scaffold)
        if [ -z "$ARG1" ]; then
            echo "Error: Module name required. Usage: ./scripts/manage.sh scaffold <module_name>"
            exit 1
        fi
        echo "Scaffolding module $ARG1 in custom_addons..."
        docker compose exec -u root web odoo scaffold "$ARG1" /mnt/extra-addons
        ;;
    update-module)
        if [ -z "$ARG1" ]; then
            echo "Error: Module name required. Usage: ./scripts/manage.sh update-module <module_name>"
            exit 1
        fi
        docker compose exec web odoo -u "$ARG1" --stop-after-init
        ;;
    *)
        echo "Usage: ./scripts/manage.sh {up|up:prod|down|down:prod|restart|logs|ps|shell|scaffold|update-module}"
        exit 1
        ;;
esac
