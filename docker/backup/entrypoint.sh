#!/bin/sh
set -eu

# crond не передаёт переменные окружения в задачи — сохраняем нужные в файл
export -p | grep -E ' (POSTGRES_|BACKUP_)' > /tmp/backup.env

echo "$BACKUP_CRON . /tmp/backup.env && sh /scripts/backup.sh > /proc/1/fd/1 2>&1" > /etc/crontabs/root
echo "[backup] расписание: '$BACKUP_CRON' (UTC), хранить последних: ${BACKUP_KEEP}"

exec crond -f -l 8
