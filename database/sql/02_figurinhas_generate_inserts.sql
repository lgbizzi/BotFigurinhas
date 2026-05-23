-- =============================================================================
-- GERAÇÃO DE INSERTs — figurinhas (banco informapromo → homelab)
--
-- PASSO 1 — Execute no banco de ORIGEM (informapromo) e redirecione a saída:
--
--   psql -h <host_origem> -U <usuario_origem> -d informapromo \
--        -t -A \
--        -f 02_figurinhas_generate_inserts.sql \
--        -o /tmp/figurinhas_inserts.sql
--
--   -t  suprime cabeçalhos e rodapés
--   -A  saída alinhada desativada (uma linha por linha de resultado)
--
-- PASSO 2 — Execute o arquivo gerado no banco de DESTINO (homelab):
--
--   psql -h <host_destino> -U lg.admin -d homelab \
--        -c "SET search_path TO \"AlbumCopa2026\";" \
--        -f /tmp/figurinhas_inserts.sql
--
-- Observações:
--   • Apenas figurinhas com quantidade > 0 são exportadas.
--   • ON CONFLICT ... DO UPDATE garante idempotência: re-executar o arquivo
--     não duplica registros, apenas atualiza quantidade e pagina.
--   • Não exporta created_at / updated_at — o destino usará NOW() nos
--     campos DEFAULT, que é suficiente para fins operacionais.
-- =============================================================================

SELECT
    'INSERT INTO figurinhas '
    || '(telegram_user_id, grupo, codigo_selecao, nome_selecao, numero, codigo_figurinha, quantidade, pagina) VALUES ('
    || telegram_user_id::text                        || ', '
    || quote_literal(grupo)                          || ', '
    || quote_literal(codigo_selecao)                 || ', '
    || quote_literal(nome_selecao)                   || ', '
    || numero::text                                  || ', '
    || quote_literal(codigo_figurinha)               || ', '
    || quantidade::text                              || ', '
    || COALESCE(pagina, 0)::text
    || ') ON CONFLICT (telegram_user_id, codigo_figurinha)'
    || ' DO UPDATE SET quantidade = EXCLUDED.quantidade,'
    || ' pagina = EXCLUDED.pagina;'
FROM public.figurinhas
WHERE quantidade > 0
ORDER BY telegram_user_id, grupo, codigo_selecao, numero;
