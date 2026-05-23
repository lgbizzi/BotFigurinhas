#!/bin/bash
# =============================================================================
# HomeLab PostgreSQL — Inicialização do banco de dados
#
# Executado automaticamente pelo container PostgreSQL na primeira inicialização
# (quando o volume pgdata está vazio). Roda como o superusuário definido em
# POSTGRES_USER (postgres).
#
# O que este script faz:
#   1. Cria o role de aplicação "lg.admin"
#   2. Cria o schema "AlbumCopa2026" e transfere a propriedade
#   3. Aplica todas as migrations em sequência dentro do schema
#   4. Concede permissões ao role de aplicação
# =============================================================================

set -e

echo "==> [HomeLab] Criando role 'lg.admin' e schema 'AlbumCopa2026'..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lg.admin') THEN
            CREATE ROLE "lg.admin" WITH LOGIN PASSWORD '1234@Bizzi';
            RAISE NOTICE 'Role lg.admin criado.';
        ELSE
            RAISE NOTICE 'Role lg.admin já existe — pulando criação.';
        END IF;
    END
    \$\$;

    CREATE SCHEMA IF NOT EXISTS "AlbumCopa2026" AUTHORIZATION "lg.admin";

    GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO "lg.admin";
    GRANT USAGE, CREATE ON SCHEMA "AlbumCopa2026" TO "lg.admin";
    ALTER ROLE "lg.admin" SET search_path TO "AlbumCopa2026";
EOSQL

echo "==> [HomeLab] Aplicando migrations no schema 'AlbumCopa2026'..."

for migration in \
    /migrations/001_initial_schema.sql \
    /migrations/002_per_user_album.sql \
    /migrations/003_add_pagina_to_figurinhas.sql \
    /migrations/004_update_pagina_values.sql
do
    echo "    -> Aplicando: $(basename "$migration")"
    PGOPTIONS='-c search_path="AlbumCopa2026"' \
        psql -v ON_ERROR_STOP=1 \
             --username "$POSTGRES_USER" \
             --dbname "$POSTGRES_DB" \
             -f "$migration"
done

echo "==> [HomeLab] Concedendo permissões ao role 'lg.admin'..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON ALL TABLES     IN SCHEMA "AlbumCopa2026" TO "lg.admin";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES  IN SCHEMA "AlbumCopa2026" TO "lg.admin";
    GRANT EXECUTE ON ALL FUNCTIONS         IN SCHEMA "AlbumCopa2026" TO "lg.admin";

    ALTER DEFAULT PRIVILEGES IN SCHEMA "AlbumCopa2026"
        GRANT ALL ON TABLES    TO "lg.admin";
    ALTER DEFAULT PRIVILEGES IN SCHEMA "AlbumCopa2026"
        GRANT ALL ON SEQUENCES TO "lg.admin";
    ALTER DEFAULT PRIVILEGES IN SCHEMA "AlbumCopa2026"
        GRANT EXECUTE ON FUNCTIONS TO "lg.admin";
EOSQL

echo "==> [HomeLab] Inicialização concluída."
