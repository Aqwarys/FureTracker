#!/bin/sh
# Делает дамп базы в /backups и оставляет только BACKUP_KEEP последних файлов.
set -euo pipefail

BACKUP_DIR=/backups
KEEP="${BACKUP_KEEP:-3}"
FILE="$BACKUP_DIR/${POSTGRES_DB}_$(date +%Y-%m-%d_%H-%M).sql.gz"

export PGPASSWORD="$POSTGRES_PASSWORD"

# Пишем во временный файл: если pg_dump упадёт, битый дамп не вытеснит старые рабочие
pg_dump -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --clean --if-exists | gzip > "$FILE.tmp"
mv "$FILE.tmp" "$FILE"
echo "[backup] $(date '+%F %T') создан $FILE ($(du -h "$FILE" | cut -f1))"

ls -1t "$BACKUP_DIR"/*.sql.gz | tail -n +"$((KEEP + 1))" | while read -r old; do
    rm -f "$old"
    echo "[backup] удалён старый $old"
done
