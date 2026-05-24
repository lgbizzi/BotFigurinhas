#!/bin/bash
# =============================================================================
# Migração de dados: informapromo → homelab (schema AlbumCopa2026)
#
# Pré-requisitos:
#   - pg_dump e psql instalados (pacote postgresql-client)
#   - Container homelab já inicializado (docker compose up -d db)
#   - Banco informapromo acessível pelo host configurado abaixo
#
# Uso:
#   chmod +x database/migrate_from_informapromo.sh
#   ./database/migrate_from_informapromo.sh
#
# As variáveis podem ser sobrescritas via .env ou diretamente no ambiente:
#   SRC_POSTGRES_PASSWORD=xxx ./database/migrate_from_informapromo.sh
# =============================================================================

set -e

# Carrega o .env se existir
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

# --- Origem ---
: "${SRC_POSTGRES_HOST:?Variável SRC_POSTGRES_HOST não definida}"
: "${SRC_POSTGRES_DB:?Variável SRC_POSTGRES_DB não definida}"
: "${SRC_POSTGRES_USER:?Variável SRC_POSTGRES_USER não definida}"
: "${SRC_POSTGRES_PASSWORD:?Variável SRC_POSTGRES_PASSWORD não definida}"

SRC_HOST="${SRC_POSTGRES_HOST}"
SRC_PORT="${SRC_POSTGRES_PORT:-5432}"
SRC_DB="${SRC_POSTGRES_DB}"
SRC_USER="${SRC_POSTGRES_USER}"
SRC_PASS="${SRC_POSTGRES_PASSWORD}"
SRC_SCHEMA="public"   # schema de origem (fixo)

# --- Destino ---
: "${POSTGRES_HOST:?Variável POSTGRES_HOST não definida}"
: "${POSTGRES_DB:?Variável POSTGRES_DB não definida}"
: "${POSTGRES_USER:?Variável POSTGRES_USER não definida}"
: "${POSTGRES_PASSWORD:?Variável POSTGRES_PASSWORD não definida}"
: "${POSTGRES_ADMIN_USER:?Variável POSTGRES_ADMIN_USER não definida}"
: "${POSTGRES_ADMIN_PASSWORD:?Variável POSTGRES_ADMIN_PASSWORD não definida}"
: "${POSTGRES_SCHEMA:?Variável POSTGRES_SCHEMA não definida}"

DST_HOST="${POSTGRES_HOST}"
DST_PORT="${POSTGRES_PORT:-5432}"
DST_DB="${POSTGRES_DB}"
DST_ADMIN_USER="${POSTGRES_ADMIN_USER}"
DST_ADMIN_PASS="${POSTGRES_ADMIN_PASSWORD}"
DST_APP_USER="${POSTGRES_USER}"
DST_APP_PASS="${POSTGRES_PASSWORD}"
DST_SCHEMA="${POSTGRES_SCHEMA}"

DUMP_FILE="/tmp/informapromo_data_$(date +%Y%m%d_%H%M%S).sql"

echo "============================================================"
echo " Migração: $SRC_DB → $DST_DB (schema: $DST_SCHEMA)"
echo "============================================================"
echo "  Origem : $SRC_USER@$SRC_HOST:$SRC_PORT/$SRC_DB"
echo "  Destino: $DST_APP_USER@$DST_HOST:$DST_PORT/$DST_DB"
echo "  Arquivo: $DUMP_FILE"
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# PASSO 1 — Exportar dados do banco informapromo (apenas dados, sem schema)
# ---------------------------------------------------------------------------
echo ""
echo "[1/4] Exportando figurinhas e movimentacoes de '$SRC_DB'..."

PGPASSWORD="$SRC_PASS" pg_dump \
    -h "$SRC_HOST" \
    -p "$SRC_PORT" \
    -U "$SRC_USER" \
    -d "$SRC_DB" \
    --data-only \
    --no-owner \
    --no-acl \
    --inserts \
    --table="${SRC_SCHEMA}.figurinhas" \
    --table="${SRC_SCHEMA}.movimentacoes" \
    -f "$DUMP_FILE"

echo "    Exportado para: $DUMP_FILE"

# ---------------------------------------------------------------------------
# PASSO 2 — Ajustar referências de schema no dump
#           public.figurinhas  → "AlbumCopa2026".figurinhas
#           public.movimentacoes → "AlbumCopa2026".movimentacoes
# ---------------------------------------------------------------------------
echo ""
echo "[2/4] Substituindo schema 'public' por '\"$DST_SCHEMA\"' no dump..."

sed -i \
    -e "s/INSERT INTO public\./INSERT INTO \"${DST_SCHEMA}\"./g" \
    -e "s/SET search_path = public/SET search_path = \"${DST_SCHEMA}\", public/g" \
    -e "s/SELECT pg_catalog\.setval('public\./SELECT pg_catalog.setval('\"${DST_SCHEMA}\"./g" \
    "$DUMP_FILE"

echo "    Substituição concluída."

# ---------------------------------------------------------------------------
# PASSO 3 — Importar dados no homelab
# ---------------------------------------------------------------------------
echo ""
echo "[3/4] Importando dados em '$DST_DB' (schema: '$DST_SCHEMA')..."

PGPASSWORD="$DST_ADMIN_PASS" psql \
    -h "$DST_HOST" \
    -p "$DST_PORT" \
    -U "$DST_ADMIN_USER" \
    -d "$DST_DB" \
    -c "SET search_path TO \"${DST_SCHEMA}\";" \
    -f "$DUMP_FILE"

echo "    Importação concluída."

# ---------------------------------------------------------------------------
# PASSO 4 — Validar dados importados (SELECT nas duas tabelas)
# ---------------------------------------------------------------------------
echo ""
echo "[4/4] Validando dados importados..."

PGPASSWORD="$DST_APP_PASS" psql \
    -h "$DST_HOST" \
    -p "$DST_PORT" \
    -U "$DST_APP_USER" \
    -d "$DST_DB" \
    -c "SET search_path TO \"${DST_SCHEMA}\";" \
    --pset="title=figurinhas — contagem por usuario" \
    -c "
        SELECT
            telegram_user_id,
            COUNT(*)                                          AS total_figurinhas,
            COUNT(*) FILTER (WHERE quantidade > 0)           AS possuidas,
            COUNT(*) FILTER (WHERE quantidade = 0)           AS faltantes,
            COALESCE(SUM(quantidade), 0)                     AS total_exemplares
        FROM \"${DST_SCHEMA}\".figurinhas
        GROUP BY telegram_user_id
        ORDER BY telegram_user_id;
    " \
    --pset="title=movimentacoes — contagem por usuario" \
    -c "
        SELECT
            telegram_user_id,
            COUNT(*)  AS total_movimentacoes,
            MIN(created_at)::date AS primeira,
            MAX(created_at)::date AS ultima
        FROM \"${DST_SCHEMA}\".movimentacoes
        GROUP BY telegram_user_id
        ORDER BY telegram_user_id;
    "

echo ""
echo "============================================================"
echo " Migração concluída com sucesso!"
echo " Dump salvo em: $DUMP_FILE"
echo "============================================================"
