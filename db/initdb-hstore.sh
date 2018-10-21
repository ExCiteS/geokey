#!/bin/sh

set -e

export PGUSER="$POSTGRES_USER"

"${psql[@]}" --dbname="template1" <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS hstore;
EOSQL

"${psql[@]}" --dbname="$POSTGRES_DB" <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS hstore;
EOSQL
