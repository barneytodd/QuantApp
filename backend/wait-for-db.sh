#!/bin/bash
set -e

DB_HOST=${DB_HOST:-db}
SA_USER=${SA_USER:-sa}  # note: SQL Server uses lowercase 'sa' by default
SA_PASSWORD=${SA_PASSWORD:-YourStrong!Passw0rd}
DB_ENGINE=${DB_ENGINE:-mssql}
TARGET_DB=${DB_NAME:-QuantDB}

echo 'Entrypoint started'

if [ "$DB_ENGINE" = "mssql" ]; then
    echo "Waiting for SQL Server at $DB_HOST..."
    until /opt/mssql-tools18/bin/sqlcmd -S "$DB_HOST" -U "$SA_USER" -P "$SA_PASSWORD" -Q "SELECT 1" -C > /dev/null 2>&1; do
        echo "SQL Server is not ready yet. Sleeping 5 seconds..."
        sleep 5
    done
    echo "✅ SQL Server is ready!"

    echo "Creating database '$TARGET_DB' ..."

    INIT_FILE="/init-db.sql"

    if [ -f "$INIT_FILE" ]; then
        echo "▶️ Running database initialization script..."
        /opt/mssql-tools18/bin/sqlcmd \
            -S "$DB_HOST" \
            -U "$SA_USER" \
            -P "$SA_PASSWORD" \
            -i "$INIT_FILE" \
            -C
        echo "✅ Initialization script executed."
    else
        echo "⚠️ No init-db.sql found at $INIT_FILE, skipping initialization."
    fi

    until /opt/mssql-tools18/bin/sqlcmd -S "$DB_HOST" -U "$SA_USER" -P "$SA_PASSWORD" \
        -C -Q "SELECT name FROM sys.databases WHERE name = '$TARGET_DB';" -h -1 | grep -q "$TARGET_DB"; do
        echo "Database '$TARGET_DB' not found yet. Sleeping 5 seconds..."
        sleep 5
    done

else
    echo "DB_ENGINE is '$DB_ENGINE'. Skipping wait-for-db (SQLite does not need it)."
fi

if [ $# -eq 0 ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
  exec "$@"
fi
