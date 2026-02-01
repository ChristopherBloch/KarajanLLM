#!/bin/bash
set -e

# Create separate database for LiteLLM to prevent schema conflicts
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE litellm;
    GRANT ALL PRIVILEGES ON DATABASE litellm TO $POSTGRES_USER;
EOSQL

echo "LiteLLM database created successfully"
