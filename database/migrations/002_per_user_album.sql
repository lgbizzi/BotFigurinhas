-- Migration 002: add telegram_user_id to figurinhas for per-user album isolation

-- 1. Remove existing rows (they have no owner)
DELETE FROM movimentacoes;
DELETE FROM figurinhas;

-- 2. Add the new column
ALTER TABLE figurinhas ADD COLUMN telegram_user_id BIGINT NOT NULL DEFAULT 0;
ALTER TABLE figurinhas ALTER COLUMN telegram_user_id DROP DEFAULT;

-- 3. Drop old single-album unique constraints
ALTER TABLE figurinhas DROP CONSTRAINT IF EXISTS figurinhas_codigo_figurinha_key;
DROP INDEX IF EXISTS uix_figurinhas_selecao_numero;

-- 4. Add per-user unique constraints
CREATE UNIQUE INDEX uix_figurinhas_user_codigo
    ON figurinhas (telegram_user_id, codigo_figurinha);

CREATE UNIQUE INDEX uix_figurinhas_user_selecao_numero
    ON figurinhas (telegram_user_id, codigo_selecao, numero);

-- 5. Index for fast per-user queries
CREATE INDEX IF NOT EXISTS ix_figurinhas_telegram_user_id
    ON figurinhas (telegram_user_id);
