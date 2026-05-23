-- =============================================================================
-- EXTRAÇÃO — figurinhas com estoque (banco informapromo / schema public)
--
-- Execute este arquivo no banco de origem (informapromo):
--
--   psql -h <host> -U <usuario> -d informapromo -f 01_figurinhas_extract.sql
--
-- O resultado mostra todas as figurinhas com quantidade > 0 agrupadas por
-- usuário, para validação antes de gerar os INSERTs.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Resumo por usuário
-- ---------------------------------------------------------------------------
SELECT
    telegram_user_id,
    COUNT(*)                                         AS total_figurinhas,
    COUNT(*) FILTER (WHERE quantidade > 0)           AS possuidas,
    COALESCE(SUM(quantidade), 0)                     AS total_exemplares,
    COUNT(*) FILTER (WHERE quantidade > 1)           AS com_repeticao
FROM public.figurinhas
GROUP BY telegram_user_id
ORDER BY telegram_user_id;

-- ---------------------------------------------------------------------------
-- 2. Detalhe completo — apenas figurinhas possuídas
-- ---------------------------------------------------------------------------
SELECT
    telegram_user_id,
    grupo,
    codigo_selecao,
    nome_selecao,
    numero,
    codigo_figurinha,
    quantidade,
    pagina
FROM public.figurinhas
WHERE quantidade > 0
ORDER BY telegram_user_id, grupo, codigo_selecao, numero;
