-- =============================================================================
-- Migration 003: add_pagina_to_figurinhas
-- Description : Add column `pagina` (physical album page number) to the
--               `figurinhas` table, create an index for ordering queries
--               (/faltantes, /repetidas), and remove the non-existent sticker
--               FWC-20 if it was previously seeded.
--
-- Idempotent   : Yes — uses IF NOT EXISTS / IF EXISTS guards throughout.
-- =============================================================================

-- 1. Add the column if it does not already exist.
ALTER TABLE figurinhas
    ADD COLUMN IF NOT EXISTS pagina SMALLINT NOT NULL DEFAULT 0;

-- 2. Create a supporting index for page-ordered queries.
CREATE INDEX IF NOT EXISTS ix_figurinhas_pagina ON figurinhas (pagina);

-- 3. Remove FWC-20, which does not exist in the physical album.
--    ON DELETE RESTRICT on movimentacoes.figurinha_id means this will raise
--    an error if any movement row references the sticker — that is intentional
--    and forces manual cleanup before proceeding.
DELETE FROM figurinhas WHERE codigo_figurinha = 'FWC-20';
