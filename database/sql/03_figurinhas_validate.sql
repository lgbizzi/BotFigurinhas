-- =============================================================================
-- VALIDAÇÃO — confirma que os dados chegaram corretamente ao homelab
--
-- Execute no banco de DESTINO (homelab) após o passo 2 acima:
--
--   psql -h <host_destino> -U lg.admin -d homelab \
--        -c "SET search_path TO \"AlbumCopa2026\";" \
--        -f 03_figurinhas_validate.sql
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Totais por usuário no destino
-- ---------------------------------------------------------------------------
SELECT
    telegram_user_id,
    COUNT(*)                                         AS total_figurinhas,
    COUNT(*) FILTER (WHERE quantidade > 0)           AS possuidas,
    COALESCE(SUM(quantidade), 0)                     AS total_exemplares
FROM figurinhas
GROUP BY telegram_user_id
ORDER BY telegram_user_id;

-- ---------------------------------------------------------------------------
-- 2. Sanidade: figurinhas com pagina = 0 (esperado apenas para FWC-0)
-- ---------------------------------------------------------------------------
SELECT codigo_figurinha, grupo, pagina, quantidade
FROM figurinhas
WHERE pagina = 0
  AND quantidade > 0
ORDER BY codigo_figurinha;
