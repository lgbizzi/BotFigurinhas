-- =============================================================================
-- Migration 004: update_pagina_values
-- Description : Backfill the `pagina` column (added in migration 003) with the
--               correct physical album page number for every existing row.
--               Rows added by migration 003 default to pagina=0; this migration
--               sets the authoritative values derived from seeds/album_data.py.
--
-- Idempotent   : Yes — UPDATE ... WHERE is safe to re-run; values are stable.
-- Safe to run  : After migration 003 has been applied.
-- =============================================================================

-- --------------------------------------------------------------------------
-- Grupo A (pages 8-14)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 8  WHERE codigo_selecao = 'MEX';
UPDATE figurinhas SET pagina = 10 WHERE codigo_selecao = 'RSA';
UPDATE figurinhas SET pagina = 12 WHERE codigo_selecao = 'KOR';
UPDATE figurinhas SET pagina = 14 WHERE codigo_selecao = 'CZE';

-- --------------------------------------------------------------------------
-- Grupo B (pages 16-22)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 16 WHERE codigo_selecao = 'CAN';
UPDATE figurinhas SET pagina = 18 WHERE codigo_selecao = 'BIH';
UPDATE figurinhas SET pagina = 20 WHERE codigo_selecao = 'QAT';
UPDATE figurinhas SET pagina = 22 WHERE codigo_selecao = 'SUI';

-- --------------------------------------------------------------------------
-- Grupo C (pages 24-30)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 24 WHERE codigo_selecao = 'BRA';
UPDATE figurinhas SET pagina = 26 WHERE codigo_selecao = 'MAR';
UPDATE figurinhas SET pagina = 28 WHERE codigo_selecao = 'HAI';
UPDATE figurinhas SET pagina = 30 WHERE codigo_selecao = 'SCO';

-- --------------------------------------------------------------------------
-- Grupo D (pages 32-38)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 32 WHERE codigo_selecao = 'USA';
UPDATE figurinhas SET pagina = 34 WHERE codigo_selecao = 'PAR';
UPDATE figurinhas SET pagina = 36 WHERE codigo_selecao = 'AUS';
UPDATE figurinhas SET pagina = 38 WHERE codigo_selecao = 'TUR';

-- --------------------------------------------------------------------------
-- Grupo E (pages 40-46)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 40 WHERE codigo_selecao = 'GER';
UPDATE figurinhas SET pagina = 42 WHERE codigo_selecao = 'CUW';
UPDATE figurinhas SET pagina = 44 WHERE codigo_selecao = 'CIV';
UPDATE figurinhas SET pagina = 46 WHERE codigo_selecao = 'ECU';

-- --------------------------------------------------------------------------
-- Grupo F (pages 48-54)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 48 WHERE codigo_selecao = 'NED';
UPDATE figurinhas SET pagina = 50 WHERE codigo_selecao = 'JPN';
UPDATE figurinhas SET pagina = 52 WHERE codigo_selecao = 'SWE';
UPDATE figurinhas SET pagina = 54 WHERE codigo_selecao = 'TUN';

-- --------------------------------------------------------------------------
-- Grupo G (pages 58-64)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 58 WHERE codigo_selecao = 'BEL';
UPDATE figurinhas SET pagina = 60 WHERE codigo_selecao = 'EGY';
UPDATE figurinhas SET pagina = 62 WHERE codigo_selecao = 'IRN';
UPDATE figurinhas SET pagina = 64 WHERE codigo_selecao = 'NZL';

-- --------------------------------------------------------------------------
-- Grupo H (pages 66-72)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 66 WHERE codigo_selecao = 'ESP';
UPDATE figurinhas SET pagina = 68 WHERE codigo_selecao = 'CPV';
UPDATE figurinhas SET pagina = 70 WHERE codigo_selecao = 'KSA';
UPDATE figurinhas SET pagina = 72 WHERE codigo_selecao = 'URU';

-- --------------------------------------------------------------------------
-- Grupo I (pages 74-80)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 74 WHERE codigo_selecao = 'FRA';
UPDATE figurinhas SET pagina = 76 WHERE codigo_selecao = 'SEN';
UPDATE figurinhas SET pagina = 78 WHERE codigo_selecao = 'IRQ';
UPDATE figurinhas SET pagina = 80 WHERE codigo_selecao = 'NOR';

-- --------------------------------------------------------------------------
-- Grupo J (pages 82-88)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 82 WHERE codigo_selecao = 'ARG';
UPDATE figurinhas SET pagina = 84 WHERE codigo_selecao = 'ALG';
UPDATE figurinhas SET pagina = 86 WHERE codigo_selecao = 'AUT';
UPDATE figurinhas SET pagina = 88 WHERE codigo_selecao = 'JOR';

-- --------------------------------------------------------------------------
-- Grupo K (pages 90-96)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 90 WHERE codigo_selecao = 'POR';
UPDATE figurinhas SET pagina = 92 WHERE codigo_selecao = 'COD';
UPDATE figurinhas SET pagina = 94 WHERE codigo_selecao = 'UZB';
UPDATE figurinhas SET pagina = 96 WHERE codigo_selecao = 'COL';

-- --------------------------------------------------------------------------
-- Grupo L (pages 98-104)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 98  WHERE codigo_selecao = 'ENG';
UPDATE figurinhas SET pagina = 100 WHERE codigo_selecao = 'CRO';
UPDATE figurinhas SET pagina = 102 WHERE codigo_selecao = 'GHA';
UPDATE figurinhas SET pagina = 104 WHERE codigo_selecao = 'PAN';

-- --------------------------------------------------------------------------
-- FWC — FIFA World Cup History (per sticker number)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 0   WHERE codigo_selecao = 'FWC' AND numero = 0;
UPDATE figurinhas SET pagina = 1   WHERE codigo_selecao = 'FWC' AND numero IN (1, 2, 3, 4);
UPDATE figurinhas SET pagina = 2   WHERE codigo_selecao = 'FWC' AND numero IN (5, 6);
UPDATE figurinhas SET pagina = 3   WHERE codigo_selecao = 'FWC' AND numero IN (7, 8);
UPDATE figurinhas SET pagina = 106 WHERE codigo_selecao = 'FWC' AND numero IN (9, 10);
UPDATE figurinhas SET pagina = 107 WHERE codigo_selecao = 'FWC' AND numero IN (11, 12, 13);
UPDATE figurinhas SET pagina = 108 WHERE codigo_selecao = 'FWC' AND numero IN (14, 15);
UPDATE figurinhas SET pagina = 109 WHERE codigo_selecao = 'FWC' AND numero IN (16, 17, 18, 19);

-- --------------------------------------------------------------------------
-- CC — Coca-Cola (per sticker number range)
-- --------------------------------------------------------------------------
UPDATE figurinhas SET pagina = 112 WHERE codigo_selecao = 'CC' AND numero BETWEEN 1 AND 6;
UPDATE figurinhas SET pagina = 113 WHERE codigo_selecao = 'CC' AND numero BETWEEN 7 AND 14;
