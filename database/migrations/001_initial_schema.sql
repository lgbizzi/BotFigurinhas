-- =============================================================================
-- Migration: 001_initial_schema
-- Description: Create figurinhas and movimentacoes tables with indexes and
--              an auto-update trigger for figurinhas.updated_at.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Table: figurinhas
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS figurinhas (
    id                SERIAL PRIMARY KEY,
    grupo             VARCHAR(3)   NOT NULL,                          -- A, B, ..., L, FWC, CC
    codigo_selecao    VARCHAR(5)   NOT NULL,
    nome_selecao      VARCHAR(60)  NOT NULL,
    numero            SMALLINT     NOT NULL,
    codigo_figurinha  VARCHAR(10)  NOT NULL UNIQUE,                   -- e.g. BRA-1, FWC-0, CC-3
    quantidade        SMALLINT     NOT NULL DEFAULT 0
                          CHECK (quantidade >= 0),
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Composite unique index: one sticker per (team, number)
CREATE UNIQUE INDEX IF NOT EXISTS uix_figurinhas_selecao_numero
    ON figurinhas (codigo_selecao, numero);

-- Index to quickly filter / aggregate by group
CREATE INDEX IF NOT EXISTS ix_figurinhas_grupo
    ON figurinhas (grupo);

-- ---------------------------------------------------------------------------
-- Table: movimentacoes
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movimentacoes (
    id                SERIAL PRIMARY KEY,
    figurinha_id      INTEGER      NOT NULL
                          REFERENCES figurinhas(id) ON DELETE RESTRICT,
    tipo              VARCHAR(10)  NOT NULL
                          CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade        SMALLINT     NOT NULL
                          CHECK (quantidade > 0),
    origem            VARCHAR(20)  NOT NULL DEFAULT 'MANUAL'
                          CHECK (origem IN ('MANUAL', 'TROCA')),
    observacao        TEXT,
    telegram_user_id  BIGINT,
    telegram_username VARCHAR(100),
    entrada_bruta     VARCHAR(100),
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for joining movimentacoes back to figurinhas
CREATE INDEX IF NOT EXISTS ix_movimentacoes_figurinha_id
    ON movimentacoes (figurinha_id);

-- Index for per-user history queries
CREATE INDEX IF NOT EXISTS ix_movimentacoes_telegram_user_id
    ON movimentacoes (telegram_user_id);

-- Index for chronological queries (most-recent-first)
CREATE INDEX IF NOT EXISTS ix_movimentacoes_created_at_desc
    ON movimentacoes (created_at DESC);

-- ---------------------------------------------------------------------------
-- Trigger: auto-update figurinhas.updated_at on every UPDATE
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_figurinhas_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_figurinhas_updated_at ON figurinhas;

CREATE TRIGGER trg_figurinhas_updated_at
BEFORE UPDATE ON figurinhas
FOR EACH ROW
EXECUTE FUNCTION fn_figurinhas_set_updated_at();
