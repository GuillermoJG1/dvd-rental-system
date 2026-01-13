#!/bin/bash
set -e

echo "Restaurando base de datos desde dvdrental.tar..."
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /docker-entrypoint-initdb.d/dvdrental.tar || true
echo "Restauración completada."