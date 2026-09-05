#!/usr/bin/env bash
# ==============================================================================
# AlamiaTravelOS - Automated Backup Script for PostgreSQL & Odoo Filestore
# ==============================================================================

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ENV_FILE="${ENV_FILE:-.env}"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

DB_USER="${DB_USER:-odoo}"
DB_NAME="${DB_NAME:-postgres}"
CONTAINER_DB="${COMPOSE_PROJECT_NAME:-alamiatravelos}_db"

mkdir -p "$BACKUP_DIR"

echo "=== Starting Backup: $TIMESTAMP ==="

# 1. Backup PostgreSQL Database
SQL_BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"
echo "Backing up database '$DB_NAME' to $SQL_BACKUP_FILE..."
docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$SQL_BACKUP_FILE"

# 2. Backup Odoo Filestore volume
FILESTORE_BACKUP_FILE="$BACKUP_DIR/filestore_${TIMESTAMP}.tar.gz"
echo "Backing up filestore volume to $FILESTORE_BACKUP_FILE..."
docker run --rm \
    --volumes-from alamiatravelos_web \
    -v "$(pwd)/$BACKUP_DIR:/backup" \
    alpine tar -czf "/backup/filestore_${TIMESTAMP}.tar.gz" -C /var/lib/odoo filestore

echo "=== Backup completed successfully ==="
echo "Files saved in: $BACKUP_DIR"
