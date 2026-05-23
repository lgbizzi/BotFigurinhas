#!/bin/bash
# =============================================================================
# HomeLab PostgreSQL — Inicialização do banco de dados
#
# Executado automaticamente pelo container PostgreSQL na primeira inicialização
# (quando o volume pgdata está vazio). Roda como o superusuário definido em
# POSTGRES_USER (variável nativa do container).
#
# Variáveis esperadas (vindas do docker-compose.yml via .env):
#   POSTGRES_USER          Superusuário do container (ex: postgres)
#   POSTGRES_DB            Nome do banco (ex: homelab)
#   POSTGRES_APP_USER      Role de aplicação (ex: lg.admin)
#   POSTGRES_APP_PASSWORD  Senha do role de aplicação
#   POSTGRES_SCHEMA        Schema do projeto (ex: AlbumCopa2026)
#
# O que este script faz:
#   1. Cria o role de aplicação ($POSTGRES_APP_USER)
#   2. Cria o schema ($POSTGRES_SCHEMA) e transfere a propriedade
#   3. Aplica todas as migrations em sequência dentro do schema
#   4. Concede permissões ao role de aplicação
# =============================================================================

set -e

: "${POSTGRES_APP_USER:?Variável POSTGRES_APP_USER não definida}"
: "${POSTGRES_APP_PASSWORD:?Variável POSTGRES_APP_PASSWORD não definida}"
: "${POSTGRES_SCHEMA:?Variável POSTGRES_SCHEMA não definida}"

echo "==> [HomeLab] Criando role '$POSTGRES_APP_USER' e schema '$POSTGRES_SCHEMA'..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$POSTGRES_APP_USER') THEN
            CREATE ROLE "$POSTGRES_APP_USER" WITH LOGIN PASSWORD '$POSTGRES_APP_PASSWORD';
            RAISE NOTICE 'Role $POSTGRES_APP_USER criado.';
        ELSE
            RAISE NOTICE 'Role $POSTGRES_APP_USER já existe — pulando criação.';
        END IF;
    END
    \$\$;

    CREATE SCHEMA IF NOT EXISTS "$POSTGRES_SCHEMA" AUTHORIZATION "$POSTGRES_APP_USER";

    GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_APP_USER";
    GRANT USAGE, CREATE ON SCHEMA "$POSTGRES_SCHEMA" TO "$POSTGRES_APP_USER";
    ALTER ROLE "$POSTGRES_APP_USER" SET search_path TO "$POSTGRES_SCHEMA";
EOSQL

echo "==> [HomeLab] Aplicando migrations no schema '$POSTGRES_SCHEMA'..."

for migration in \
    /migrations/001_initial_schema.sql \
    /migrations/002_per_user_album.sql \
    /migrations/003_add_pagina_to_figurinhas.sql \
    /migrations/004_update_pagina_values.sql
do
    echo "    -> Aplicando: $(basename "$migration")"
    PGOPTIONS="-c search_path=\"$POSTGRES_SCHEMA\"" \
        psql -v ON_ERROR_STOP=1 \
             --username "$POSTGRES_USER" \
             --dbname "$POSTGRES_DB" \
             -f "$migration"
done

echo "==> [HomeLab] Concedendo permissões ao role '$POSTGRES_APP_USER'..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA "$POSTGRES_SCHEMA" TO "$POSTGRES_APP_USER";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA "$POSTGRES_SCHEMA" TO "$POSTGRES_APP_USER";
    GRANT EXECUTE ON ALL FUNCTIONS        IN SCHEMA "$POSTGRES_SCHEMA" TO "$POSTGRES_APP_USER";

    ALTER DEFAULT PRIVILEGES IN SCHEMA "$POSTGRES_SCHEMA"
        GRANT ALL ON TABLES    TO "$POSTGRES_APP_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA "$POSTGRES_SCHEMA"
        GRANT ALL ON SEQUENCES TO "$POSTGRES_APP_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA "$POSTGRES_SCHEMA"
        GRANT EXECUTE ON FUNCTIONS TO "$POSTGRES_APP_USER";
EOSQL

echo "==> [HomeLab] Inicialização concluída."
