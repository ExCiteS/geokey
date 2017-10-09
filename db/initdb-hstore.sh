#!/bin/sh

set -e

export PGUSER="$POSTGRES_USER"

echo "Adding hstore extension to $DB"
"${psql[@]}" --dbname="$POSTGRES_DB" <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS hstore;
EOSQL
