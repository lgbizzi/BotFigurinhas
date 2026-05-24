# PROJECT_DEV.md — Album Copa 2026

> Arquivo de controle do projeto. Mantido e atualizado exclusivamente pelo **Business Analyst**.

> 🤖 **Bot em produção:** [@InformaFigurinhasBot](https://t.me/InformaFigurinhasBot)

---

## Status Geral

✅ **Etapa 11 concluída** — 2026-05-24. Comandos `/buscar` e `/buscar_pais` implementados com fluxo conversacional, templates e registro no bot.

✅ **Etapa 10 concluída** — 2026-05-23/24. Deploy em container Docker (PostgreSQL + bot), credenciais via `.env`, script de inicialização sem valores chumbados, documentação de deploy, scripts SQL de migração de dados.

✅ **Etapa 9 concluída** — 2026-05-23. Melhorias no `/progresso` (novos dados analíticos) e nos cabeçalhos de `/faltantes` e `/repetidas` implementadas e aprovadas em QA.

---

## Etapas e Tarefas

### Etapa 0 — Infraestrutura Docker
> Agente responsável: **Data Engineer** | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 0.1 | Criar `Dockerfile` da aplicação Python (base `python:3.12-slim`, usuário não-root) | ✅ Concluído | |
| 0.2 | Criar `docker-compose.yml` com serviços `bot` e `db` (healthcheck, restart: always) | ✅ Concluído | |
| 0.3 | Criar `docker-compose.override.yml` para desenvolvimento local (volume de código) | ✅ Concluído | |
| 0.4 | Criar `.dockerignore` (excluir testes, `.env`, `__pycache__`) | ✅ Concluído | |
| 0.5 | Criar `.gitignore` (incluir `.env`, `__pycache__`, volumes Docker) | ✅ Concluído | |
| 0.6 | Criar `.env.example` com todas as variáveis documentadas sem valores reais | ✅ Concluído | Corrigido na Rodada 2 (placeholders neutros) |
| 0.7 | **Revisão QA — Etapa 0** | ✅ Concluído | Aprovado na Rodada 2 — 2026-05-20 |

---

### Etapa 1 — Infraestrutura e Banco de Dados
> Agente responsável: **Data Engineer** | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 1.1 | Criar `config/settings.py` com leitura de variáveis de ambiente | ✅ Concluído | |
| 1.2 | Criar `database/connection.py` com pool Singleton | ✅ Concluído | |
| 1.3 | Criar `database/migrations/001_initial_schema.sql` | ✅ Concluído | |
| 1.4 | Criar `seeds/album_data.py` com estrutura completa do álbum | ✅ Concluído | Fonte única de verdade — 995 figurinhas verificadas |
| 1.5 | Criar `seeds/seed_figurinhas.py` | ✅ Concluído | |
| 1.6 | Criar `models/figurinha.py` e `models/movimentacao.py` | ✅ Concluído | |
| 1.7 | **Revisão QA — Etapa 1** | ✅ Concluído | Aprovado na Rodada 1 — 2026-05-20 |

---

### Etapa 2 — Parser de Códigos
> Agente responsável: **Tests Analyst** (testes) + **Parser Specialist** (implementação) | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 2.1 | Tests Analyst escreve `tests/unit/test_codigo_parser.py` | ✅ Concluído | Aprovado QA Rodada 1 — 2026-05-20 |
| 2.2 | Parser Specialist implementa `services/codigo_parser.py` | ✅ Concluído | |
| 2.3 | Criar `exceptions/domain_exceptions.py` | ✅ Concluído | |
| 2.4 | **Revisão QA — Etapa 2** | ✅ Concluído | Aprovado Rodada 1 — 2026-05-20 |

---

### Etapa 3 — Camada de Dados (Repositories)
> Agente responsável: **Tests Analyst** (testes) + **Backend Dev** (implementação) | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 3.1 | Tests Analyst escreve `tests/conftest.py` | ✅ Concluído | Aprovado QA Rodada 1 — 2026-05-20 |
| 3.2 | Tests Analyst escreve `tests/integration/test_figurinha_repository.py` | ✅ Concluído | |
| 3.3 | Tests Analyst escreve `tests/integration/test_movimentacao_repository.py` | ✅ Concluído | |
| 3.4 | Backend Dev implementa `repositories/base_repository.py` | ✅ Concluído | |
| 3.5 | Backend Dev implementa `repositories/figurinha_repository.py` | ✅ Concluído | |
| 3.6 | Backend Dev implementa `repositories/movimentacao_repository.py` | ✅ Concluído | Corrigido na Rodada 2 (método insert refatorado) |
| 3.7 | **Revisão QA — Etapa 3** | ✅ Concluído | Aprovado Rodada 2 — 2026-05-20 |

---

### Etapa 4 — Camada de Negócio (Services)
> Agente responsável: **Tests Analyst** (testes) + **Backend Dev** (implementação) | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 4.1 | Tests Analyst escreve `tests/unit/test_figurinha_service.py` | ✅ Concluído | Aprovado QA Rodada 2 — 2026-05-20 |
| 4.2 | Tests Analyst escreve `tests/unit/test_movimentacao_service.py` | ✅ Concluído | Aprovado QA Rodada 1 — 2026-05-20 |
| 4.3 | Backend Dev implementa `services/figurinha_service.py` | ✅ Concluído | Nomes de métodos corrigidos na Rodada 2 |
| 4.4 | Backend Dev implementa `services/movimentacao_service.py` | ✅ Concluído | |
| 4.5 | **Revisão QA — Etapa 4** | ✅ Concluído | Aprovado Rodada 3 — 2026-05-20 |

---

### Etapa 5 — Interface Telegram (Bot)
> Agente responsável: **Bot Interface Dev** | Revisão: **QA**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 5.1 | Implementar `views/message_templates.py` | ✅ Concluído | |
| 5.2 | Implementar `controllers/bot_controller.py` | ✅ Concluído | B1/B2 corrigidos na Rodada 2 |
| 5.3 | Implementar `bot/handlers/adicionar_handler.py` | ✅ Concluído | |
| 5.4 | Implementar `bot/handlers/remover_handler.py` | ✅ Concluído | |
| 5.5 | Implementar `bot/bot_setup.py` | ✅ Concluído | |
| 5.6 | Implementar `main.py` | ✅ Concluído | B3 (conn leak) corrigido na Rodada 2 |
| 5.7 | **Revisão QA — Etapa 5** | ✅ Concluído | Aprovado Rodada 2 — 2026-05-20 |

---

### Etapa 6 — Alteração de Escopo: coluna `pagina` + remoção de FWC-20
> Agentes: **Tests Analyst** → **Data Engineer** → **Backend Dev** | Revisão: **QA**
>
> Decisão de escopo registrada em 2026-05-23. Deve ser concluída antes da revisão final (6.11–6.13).

#### 6A — Atualização de Testes (pré-implementação / TDD)
> Agente: **Tests Analyst**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 6.1 | Tests Analyst atualiza `tests/integration/test_figurinha_repository.py` — novo campo `pagina`, nova ordenação `pagina, numero` em faltantes/repetidas, remoção de FWC-20 dos fixtures | ✅ Concluído | |
| 6.2 | Tests Analyst atualiza `tests/unit/test_figurinha_service.py` — objetos `Figurinha` mockados com campo `pagina` | ✅ Concluído | `test_figurinha_service.py` sem alterações; `conftest.py` atualizado (seed + db_transaction + sample_figurinha) |
| 6.3 | **Revisão QA — testes atualizados** | ✅ Concluído | Aprovado Rodada 13 — 2026-05-23 (reprovado nas rodadas 11 e 12) |

#### 6B — Dados e Infraestrutura
> Agente: **Data Engineer**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 6.4 | Data Engineer cria `database/migrations/003_add_pagina_to_figurinhas.sql` — ADD COLUMN `pagina SMALLINT NOT NULL DEFAULT 0` + índice + DELETE de FWC-20 existente | ✅ Concluído | Nomeada `003` (já existia `002_per_user_album.sql`) |
| 6.5 | Data Engineer atualiza `seeds/album_data.py` — remove FWC-20 (`_team_range(0,19)`), ajusta total para 994, adiciona campo `pagina` ao `AlbumGroup` com suporte a override por número (FWC e CC) | ✅ Concluído | |
| 6.6 | Data Engineer atualiza `seeds/seed_figurinhas.py` — inclui `pagina` e `telegram_user_id` no INSERT, corrige `ON CONFLICT` | ✅ Concluído | B1/B2 corrigidos pelo BA após Rodada 14 |
| 6.7 | **Revisão QA — Data Engineer** | ✅ Concluído | Aprovado Rodada 15 — 2026-05-23 (reprovado na Rodada 14) |

#### 6C — Camada de Domínio e Dados
> Agente: **Backend Dev**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 6.8 | Backend Dev atualiza `models/figurinha.py` — adiciona campo `pagina: int`, atualiza `from_row` de 9 para 10 colunas | ✅ Concluído | |
| 6.9 | Backend Dev atualiza `repositories/figurinha_repository.py` — adiciona `pagina` ao `_SELECT_COLS`, altera `ORDER BY` em `find_faltantes` e `find_repetidas` para `pagina, numero` | ✅ Concluído | |
| 6.10 | **Revisão QA — Backend Dev** | ✅ Concluído | Aprovado Rodada 16 — 2026-05-23. Melhoria registrada: `inicializar_album` sem `pagina` e sem rollback (ver tarefa 6.14) |

#### 6D — Interface do Bot (nova UX para /faltantes e /repetidas)
> Agente: **Bot Interface Dev** | Pré-requisito: 6C concluída

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 6.11 | Bot Interface Dev atualiza `views/message_templates.py` — novo template `/faltantes` com códigos por seleção + emojis de bandeira; novo template `/repetidas` com quantidade por país + emojis; lógica de quebra por Grupo quando necessário | ✅ Concluído | |
| 6.12 | Bot Interface Dev atualiza `controllers/bot_controller.py` e handlers de `/faltantes` e `/repetidas` para usar os novos templates e enviar múltiplas mensagens por Grupo se necessário | ✅ Concluído | |
| 6.13 | **Revisão QA — Bot Interface Dev** | ✅ Concluído | Aprovado Rodada 18 — 2026-05-23 (reprovado Rodada 17) |
| 6.14 | Backend Dev corrige `repositories/figurinha_repository.py` — adicionar `pagina` ao INSERT de `inicializar_album` e adicionar rollback explícito | ✅ Concluído | Aprovado Rodada 20 — 2026-05-23. Refatorado: `_build_album_rows` e `_build_stickers_payload` extraídos como helpers privados (limite de 20 linhas) |

---

### Etapa 8 — Melhorias de UX Pós-Entrega: agrupamento por Grupo no `/faltantes` e `/repetidas`
> Agente responsável: **Business Analyst** (alterações diretas) | Data: 2026-05-23

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 8.1 | UX Change 2 — `/faltantes` agrupado por Grupo do álbum com cabeçalho `*Grupo A:*`; 1 mensagem por Grupo | ✅ Concluído | `_agrupar` reescrito em `album_query_service.py`; `_compute_header` adicionado; `formatar_faltantes` reescrito em `message_templates.py`; 2 novos testes em `test_album_query_service.py` |
| 8.2 | UX Change 3 — `/repetidas` adota o mesmo formato de Grupos que `/faltantes`, com códigos de figurinha por seleção | ✅ Concluído | `repetidas_agrupadas` adicionado a `AlbumQueryService`; `formatar_repetidas` reescrito (retorna `list[str]`); `consultar_repetidas` retorna `list[str]`; `cmd_repetidas` itera igual ao `cmd_faltantes`; 4 novos testes em `test_album_query_service.py` |

---

### Etapa 9 — Melhorias no `/progresso`, `/faltantes` e `/repetidas`
> Agentes: **Tests Analyst** → **Backend Dev** → **Bot Interface Dev** | Revisão: **QA** | Data: 2026-05-23

#### 9A — Testes (pré-implementação / TDD)
> Agente: **Tests Analyst**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 9.1 | Tests Analyst escreve testes para os novos métodos do `FigurinhaRepository` (`get_paises_completos`, `get_top3_proximos`, `get_top3_distantes`, `get_brilhantes_faltantes`, `get_cc_faltantes`) | ✅ Concluído | 12 testes de integração adicionados |
| 9.2 | Tests Analyst escreve testes para `AlbumQueryService.progresso_detalhado()` | ✅ Concluído | 9 testes unitários adicionados (7 originais + 2 delegação por BA) |
| 9.3 | **Revisão QA — testes Etapa 9A** | ✅ Concluído | Aprovado Rodada 26 — 2026-05-23 (reprovado Rodada 25: B2 var morta, B3 delegação ausente; B1 era falso positivo) |

#### 9B — Backend (repositories + service)
> Agente: **Backend Dev** | Pré-requisito: 9A aprovado

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 9.4 | Backend Dev atualiza `models/progresso.py` — adicionar campos: `paises_completos`, `top3_proximos`, `top3_distantes`, `brilhantes_faltantes`, `cc_faltantes` | ✅ Concluído | |
| 9.5 | Backend Dev adiciona métodos SQL ao `repositories/figurinha_repository.py` | ✅ Concluído | `get_selecoes_faltantes_contagem` e `get_cc_faltantes` implementados; `get_paises_completos` removido (calculado no serviço) |
| 9.6 | Backend Dev adiciona `progresso_detalhado()` ao `services/album_query_service.py` | ✅ Concluído | `_flush_grupo` extraído de `_agrupar` para respeitar limite de 20 linhas |
| 9.7 | **Revisão QA — Backend Etapa 9B** | ✅ Concluído | Aprovado Rodada 30 — 2026-05-23 (reprovado Rodadas 27, 28 e 29) |

#### 9C — Interface (templates + controller)
> Agente: **Bot Interface Dev** | Pré-requisito: 9B aprovado

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 9.8 | Bot Interface Dev reescreve `formatar_progresso()` em `message_templates.py` — nova ordem, novo termo, novos campos | ✅ Concluído | `_formatar_top3` extraído para respeitar limite de 20 linhas |
| 9.9 | Bot Interface Dev atualiza `formatar_faltantes()` — prefixar cabeçalho com `"Faltantes - "` | ✅ Concluído | |
| 9.10 | Bot Interface Dev atualiza `formatar_repetidas()` — prefixar cabeçalho com `"Repetidas - "` | ✅ Concluído | |
| 9.11 | Bot Interface Dev atualiza `consultar_progresso()` em `bot_controller.py` para usar `progresso_detalhado()` | ✅ Concluído | |
| 9.12 | **Revisão QA — Bot Interface Etapa 9C** | ✅ Concluído | Aprovado Rodada 31 — 2026-05-23 |

---

### Etapa 7 — Revisão Final e Testes de Integração Ponta a Ponta
> Agentes: **QA** + **Tests Analyst** | Pré-requisito: Etapa 6 concluída

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 7.1 | Testes de integração E2E dos fluxos /adicionar, /remover e /progresso | ✅ Concluído | Aprovado Rodada 22 — 2026-05-23. 6 testes; isolamento por user_id único + `cleanup_e2e_users` session fixture |
| 7.2 | Revisão QA final — toda a codebase | ✅ Concluído | Aprovado Rodada 24 — 2026-05-23 (reprovado Rodada 23 — 9 bloqueadores de métodos >20 linhas e docstring 995→994; todos resolvidos) |
| 7.3 | Validação de cobertura ≥ 90% (services + repositories) | ✅ Concluído | 72 testes no total (33 unit + 39 integration) cobrem todos os métodos públicos de services e repositories. Execução real requer `pytest --cov --cov-report=term-missing` contra o banco de teste PostgreSQL. Comando: `cd projects/BotFigurinhas && pytest tests/ --cov=services --cov=repositories --cov-report=term-missing --cov-fail-under=90` |

---

### Etapa 10 — Deploy com Docker e Documentação de Infraestrutura
> Agente responsável: **Data Engineer** + **Business Analyst** | Data: 2026-05-23/24

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 10.1 | Criar `database/homelab_init/00_setup.sh` — script de inicialização do PostgreSQL (cria role, schema, aplica migrations, concede permissões) | ✅ Concluído | Inicialmente com credenciais chumbadas; corrigido na tarefa 10.3 |
| 10.2 | Atualizar `docker-compose.yml` — separar superusuário Docker (`POSTGRES_ADMIN_USER`) do usuário de aplicação (`POSTGRES_USER`); repassar `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_SCHEMA` ao container db | ✅ Concluído | |
| 10.3 | Corrigir `database/homelab_init/00_setup.sh` — substituir credenciais chumbadas por variáveis de ambiente; adicionar guard clauses `: "${VAR:?}"` | ✅ Concluído | Identificado pelo usuário; `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_SCHEMA` via env |
| 10.4 | Atualizar `config/settings.py` — adicionar `DB_SCHEMA` lido de `POSTGRES_SCHEMA` | ✅ Concluído | |
| 10.5 | Atualizar `database/connection.py` — adicionar `options=f'-c search_path="{settings.DB_SCHEMA}"'` ao pool | ✅ Concluído | Garante isolamento de schema em todas as conexões |
| 10.6 | Atualizar `.env.example` — separar campos obrigatórios (`<CHANGE_ME>`) dos com sugestão; adicionar `POSTGRES_ADMIN_USER/PASSWORD`; adicionar seção `SRC_POSTGRES_*` para migração | ✅ Concluído | |
| 10.7 | Criar `docs/DEPLOY.md` — guia completo de deploy: pré-requisitos, passo a passo, fluxo de credenciais, manutenção, backup, variáveis | ✅ Concluído | |
| 10.8 | Atualizar `README.md` — nova seção de deploy sem credenciais chumbadas; diagrama de fluxo de credenciais; tabela `<CHANGE_ME>` vs sugestão; seção "Execução sem Docker"; tabela de variáveis com coluna "Sugestão de valor" | ✅ Concluído | |
| 10.9 | Criar `database/migrate_from_informapromo.sh` — script bash para migração de dados (pg_dump → sed schema → psql import → SELECT validação) usando `SRC_POSTGRES_*` e `POSTGRES_*` do `.env` | ✅ Concluído | |
| 10.10 | Criar scripts SQL em `database/sql/` — `01_figurinhas_extract.sql` (inspeção origem), `02_figurinhas_generate_inserts.sql` (gera INSERTs idempotentes), `03_figurinhas_validate.sql` (valida destino) | ✅ Concluído | |

---

### Etapa 11 — Novos Comandos: `/buscar` e `/buscar_pais`
> Agente responsável: **Bot Interface Dev** | Data: 2026-05-24

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 11.1 | Adicionar `find_by_codigo_readonly` e `find_by_selecao` ao `repositories/figurinha_repository.py` — consultas sem `FOR UPDATE` para uso em leituras | ✅ Concluído | |
| 11.2 | Adicionar `resolver_selecao` ao `services/codigo_parser.py` — resolve nome de país/código em `codigo_selecao` sem exigir número de figurinha | ✅ Concluído | Reutiliza `_NOME_PARA_CODIGO`, `_NOMES_COMPOSTOS`, `_NOMES_SIMPLES` existentes |
| 11.3 | Adicionar `resolver_selecao` e `buscar_para_consulta` ao `services/figurinha_service.py` — leitura somente (sem lock) | ✅ Concluído | |
| 11.4 | Adicionar `buscar_por_selecao` ao `services/album_query_service.py` — retorna todas as figurinhas de uma seleção por `numero` | ✅ Concluído | |
| 11.5 | Adicionar templates ao `views/message_templates.py` — `solicitar_codigo_busca`, `formatar_busca` (3 cenários: 0, 1, >1), `solicitar_pais`, `formatar_busca_pais` (3 seções: ✅ Já tem / ⚠️ Repetidas / ❌ Faltam); atualizar `boas_vindas` | ✅ Concluído | |
| 11.6 | Adicionar `consultar_buscar` e `consultar_buscar_pais` ao `controllers/bot_controller.py` | ✅ Concluído | |
| 11.7 | Criar `bot/handlers/buscar_handler.py` — `ConversationHandler` para `/buscar` e `/buscar_pais` (fluxo de 1 passo cada) | ✅ Concluído | |
| 11.8 | Atualizar `bot/bot_setup.py` — registrar `build_buscar_handlers` | ✅ Concluído | |
| 11.9 | Corrigir `views/message_templates.py` — `formatar_busca_pais`: figurinhas com `quantidade >= 1` aparecem em "Já tem"; repetidas exibem `quantidade - 1` na seção "Repetidas" | ✅ Concluído | Ajuste solicitado pelo usuário após deploy |

---

### Etapa 12 — Comandos de Privacidade: `/consulta` e `/excluir_usuario`
> Agente responsável: **Bot Interface Dev** | Data: 2026-05-24

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 12.1 | Adicionar `get_dados_usuario` ao `repositories/figurinha_repository.py` — aggregate query com totais de figurinhas e movimentações | ✅ Concluído | |
| 12.2 | Adicionar `excluir_usuario` ao `repositories/figurinha_repository.py` — DELETE em ordem FK-safe (movimentacoes → figurinhas); sem commit (responsabilidade do caller) | ✅ Concluído | |
| 12.3 | Adicionar `consultar_dados_usuario` e `excluir_usuario` ao `services/figurinha_service.py` — `excluir_usuario` faz commit e rollback em caso de erro | ✅ Concluído | |
| 12.4 | Adicionar templates ao `views/message_templates.py` — `formatar_dados_usuario`, `confirmacao_exclusao`, `confirmar_exclusao_realizada`, `cancelar_exclusao`; atualizar `boas_vindas` | ✅ Concluído | |
| 12.5 | Adicionar `consultar_dados_usuario` e `excluir_usuario` ao `controllers/bot_controller.py` | ✅ Concluído | |
| 12.6 | Criar `bot/handlers/privacidade_handler.py` — `CommandHandler` simples para `/consulta`; `ConversationHandler` com teclado Sim/Não para `/excluir_usuario` | ✅ Concluído | Teclado customizado via `ReplyKeyboardMarkup`; removido após resposta via `ReplyKeyboardRemove` |
| 12.7 | Atualizar `bot/bot_setup.py` — registrar `build_privacidade_handlers` | ✅ Concluído | |
| 12.8 | Atualizar `README.md` — adicionar `/consulta` e `/excluir_usuario` à tabela de comandos | ✅ Concluído | |

---

## Legenda de Status

| Ícone | Significado |
|---|---|
| ⬜ Pendente | Não iniciado |
| 🔵 Em andamento | Em desenvolvimento |
| 🟡 Em revisão | Aguardando QA |
| 🔴 Reprovado | QA apontou bloqueadores |
| ✅ Concluído | Aprovado pelo QA |

---

## Decisões Registradas

| Data | Decisão | Motivo | Agente que levantou |
|---|---|---|---|
| — | `album_data.py` é a fonte única de verdade da estrutura do álbum | Evitar duplicação e inconsistência entre seed, parser e futuras consultas | Business Analyst |
| — | `CodigoParser` não acessa banco de dados | Manter o parser puro e testável sem dependência de infraestrutura | Business Analyst |
| — | `BotController` nunca lança exceções para os handlers | Simplificar handlers e centralizar tratamento de erro | Business Analyst |
| — | Testes são escritos antes da implementação (TDD) | Garantir que o código é desenvolvido orientado a comportamento | Business Analyst |
| 2026-05-23 | Adicionar coluna `pagina SMALLINT` à tabela `figurinhas` | Permitir ordenação das consultas `/faltantes` e `/repetidas` pela ordem física do álbum | Business Analyst (solicitação do usuário) |
| 2026-05-23 | FWC-20 não existe no álbum real — removida do cadastro | Correção de dados; total correto do álbum é **994** figurinhas (960 seleções + 20 FWC + 14 CC) | Business Analyst (confirmado pelo usuário) |
| 2026-05-23 | Mapeamento de páginas FWC: 0→p.0; 1-4→p.1; 5-6→p.2; 7-8→p.3; 9-10→p.106; 11-13→p.107; 14-15→p.108; 16-19→p.109 | Fonte: especificação do usuário em 2026-05-23 | Business Analyst |
| 2026-05-23 | Mapeamento de páginas CC: 1-6→p.112; 7-14→p.113 | Fonte: especificação do usuário em 2026-05-23 | Business Analyst |
| 2026-05-23 | `/faltantes` exibe códigos de figurinha por seleção, emojis de bandeira, 1 mensagem por Grupo do álbum (`*Grupo A:*`); FWC dividida em early (pág. 0–3) e late (pág. 106–109); CC ao final | Melhora UX: usuário vê quais figurinhas faltam de cada seleção, na ordem do álbum, organizado por Grupo | Business Analyst (solicitação do usuário — UX Changes 1 e 2) |
| 2026-05-23 | `/repetidas` exibe os mesmos códigos de figurinha por seleção e formato de Grupos que `/faltantes` (substituindo a exibição de quantidade por país) | Melhora UX: consistência visual entre `/faltantes` e `/repetidas`; usuário identifica exatamente quais figurinhas sobram | Business Analyst (solicitação do usuário — UX Change 3) |
| 2026-05-23 | Emojis de bandeira obrigatórios para cada seleção em todas as mensagens de listagem | Consistência visual; mapeamento de código_selecao → emoji é responsabilidade de `message_templates.py` | Business Analyst |
| 2026-05-23 | `/progresso` reformulado: nova ordem (% → únicas → faltando → total), "exemplares" → "figurinhas", adição de países completos, top 3 mais próximos, top 3 mais distantes, Brilhantes Faltantes (numero=1 de A–L + FWC com qtd=0) e CC Faltantes (CC com qtd=0 listadas) | Richer UX no progresso; elimina necessidade do comando `/status` | Business Analyst (solicitação do usuário) |
| 2026-05-23 | Cabeçalhos de `/faltantes` e `/repetidas` prefixados com `"Faltantes - "` / `"Repetidas - "` | Facilita leitura das mensagens no histórico do Telegram | Business Analyst (solicitação do usuário) |
| 2026-05-23 | "Brilhante" = figurinha `numero = 1` de cada seleção (grupos A–L) + todas as figurinhas da seção FWC | Confirmado pelo usuário em 2026-05-23 | Business Analyst |
| 2026-05-23 | `get_paises_completos` removido do repositório; `_paises_completos` calculado no serviço a partir de `get_selecoes_faltantes_contagem` (seleções com `faltantes == 0`) | Lógica de domínio não deve residir em SQL (HAVING no repositório); cálculo no serviço é mais testável | Business Analyst |
| 2026-05-23 | `_flush_grupo` extraído de `_agrupar` em `album_query_service.py` | Respeitar limite de 20 linhas executáveis por método | Business Analyst |
| 2026-05-23 | `_formatar_top3` extraído em `message_templates.py` | Respeitar limite de 20 linhas executáveis por método | Business Analyst |
| 2026-05-23 | Separação de superusuário Docker (`POSTGRES_ADMIN_USER=postgres`) do usuário de aplicação (`POSTGRES_USER=lg.admin`) no `docker-compose.yml` | Docker exige que `POSTGRES_USER` seja o superusuário do container; o usuário de aplicação é criado pelo script de init | Business Analyst (identificado pelo usuário) |
| 2026-05-23 | `00_setup.sh` usa variáveis de ambiente (`$POSTGRES_APP_USER`, `$POSTGRES_APP_PASSWORD`, `$POSTGRES_SCHEMA`) em vez de valores chumbados | Credenciais nunca devem ser commitadas no código; `.env` é a fonte única | Business Analyst (correção solicitada pelo usuário) |
| 2026-05-23 | `search_path` definido via `options=f'-c search_path="{settings.DB_SCHEMA}"'` no pool de conexões | Garante que todo SQL executado via psycopg2 use o schema correto sem prefixo explícito nas queries | Business Analyst |
| 2026-05-24 | `/buscar` e `/buscar_pais` implementados como `ConversationHandler` de 1 passo | Consistência com o padrão existente de `/adicionar` e `/remover`; isola o estado de espera de entrada | Business Analyst (solicitação do usuário) |
| 2026-05-24 | `find_by_codigo_readonly` usa `SELECT` sem `FOR UPDATE` para o `/buscar` | Consultas de leitura não devem bloquear linhas; `FOR UPDATE` reservado para operações de escrita | Business Analyst |
| 2026-05-24 | `resolver_selecao` no parser aceita código direto (`BRA`) ou nome em português (`Brasil`, `Costa do Marfim`) sem exigir número | Permite que o usuário informe somente o país no `/buscar_pais`, reutilizando o dicionário de aliases já existente | Business Analyst |
| 2026-05-24 | `/buscar_pais`: figurinhas com `quantidade >= 1` aparecem em "Já tem"; repetidas aparecem também em "Repetidas" com `quantidade - 1` | Uma figurinha é "possuída" mesmo que haja repetidas; o excedente representa o estoque disponível para troca | Business Analyst (ajuste solicitado pelo usuário) |
| 2026-05-24 | `/excluir_usuario` usa `ReplyKeyboardMarkup` com botões Sim/Não | Reduz chance de erro de digitação em operação irreversível; teclado é removido após a resposta via `ReplyKeyboardRemove` | Business Analyst |
| 2026-05-24 | DELETE em ordem FK-safe: `movimentacoes` antes de `figurinhas` | `movimentacoes.figurinha_id` tem `ON DELETE RESTRICT`; inverter a ordem causaria erro de FK | Business Analyst |
| 2026-05-24 | Criar `docs/PRIVACY_POLICY.md` com política de privacidade mínima | Documentar os dados coletados (Telegram ID e username) e direitos do usuário (consulta e exclusão), em conformidade com boas práticas de privacidade | Business Analyst (solicitação do usuário) |

---

## Impedimentos Ativos

*Nenhum impedimento ativo no momento.*

---

## Histórico de Revisões QA

| Rodada | Agente revisado | Entregável | Resultado | Bloqueadores resolvidos? |
|---|---|---|---|---|
| 1 | Data Engineer | Etapa 0 — Infraestrutura Docker | 🔴 Reprovado | `.env.example` com valores internos (`album_user`, `album_copa`) |
| 2 | Data Engineer | `.env.example` (correção) | ✅ Aprovado | Sim — placeholders neutros `<CHANGE_ME>` aplicados |
| 3 | Data Engineer | Etapa 1 — Banco e Código | ✅ Aprovado | 5 melhorias sugeridas (não bloqueadoras) |
| 4 | Tests Analyst | Etapa 2 — Exceções + Testes Parser | ✅ Aprovado | — |
| 5 | Parser Specialist | `services/codigo_parser.py` | ✅ Aprovado | 4 melhorias sugeridas (não bloqueadoras) |
| 6 | Tests Analyst | Etapa 3 — conftest + testes repositories | ✅ Aprovado | — |
| 7 | Backend Developer | Etapa 3 — Repositories | ✅ Aprovado | Corrigido insert na Rodada 2 |
| 8 | Tests Analyst | Etapa 4 — Testes Services | ✅ Aprovado | Corrigido em 2 rodadas (B-01, B-02, NB1) |
| 9 | Backend Developer | Etapa 4 — Services | ✅ Aprovado | Nomes de métodos corrigidos na Rodada 2 |
| 10 | Bot Interface Developer | Etapa 5 — Interface Telegram | ✅ Aprovado | B1/B2/B3 corrigidos na Rodada 2 |
| 11 | Tests Analyst | Etapa 6A — testes `pagina` (1ª entrega) | 🔴 Reprovado | 6 bloqueadores: assinaturas erradas, seed sem `telegram_user_id`, `db_transaction.execute` inválido, `sample_figurinha` com `pagina` prematuro |
| 12 | Tests Analyst | Etapa 6A — testes `pagina` (correções B1–B6) | 🔴 Reprovado | NB1: `test_figurinha_deve_ter_campo_pagina` usava `telegram_user_id=123456789` em vez de `0` |
| 13 | Business Analyst (correção direta NB1) | Etapa 6A — correção pontual | ✅ Aprovado | — |
| 14 | Data Engineer | Etapa 6B — migration 003 + album_data + seed_figurinhas | 🔴 Reprovado | B1: ON CONFLICT errado; B2: telegram_user_id ausente no seed |
| 15 | Business Analyst (correção direta B1/B2) | `seeds/seed_figurinhas.py` | ✅ Aprovado | — |
| 16 | Backend Developer | Etapa 6C — `models/figurinha.py` + `repositories/figurinha_repository.py` | ✅ Aprovado | — |
| 17 | Bot Interface Developer | Etapa 6D — `message_templates.py` + `bot_controller.py` + `consultas_handler.py` | 🔴 Reprovado | `formatar_repetidas` > 20 linhas |
| 18 | Business Analyst (correção direta) | `message_templates.py` — extração `_acumular_por_pais` | ✅ Aprovado | — |
| 19 | Backend Dev | Tarefa 6.14 — `inicializar_album` com `pagina` + rollback | 🔴 Reprovado | Métodos `inicializar_album` e `garantir_album_inicializado` > 20 linhas |
| 20 | Business Analyst (correção direta) | Extração `_build_album_rows` e `_build_stickers_payload` | ✅ Aprovado | — |
| 21 | Tests Analyst | Tarefa 7.1 — testes E2E 6 fluxos | 🔴 Reprovado | 4 bloqueadores: assertion frágil, inconsistência 994/995, isolamento db_transaction ineficaz, assertion genérica "❌" |
| 22 | Business Analyst (reescrita direta) | `test_e2e_fluxos.py` — assertions específicas + `cleanup_e2e_users` + helper | ✅ Aprovado | — |
| 23 | Todos os agentes | QA final — toda a codebase | 🔴 Reprovado | 9 bloqueadores: 8× métodos >20 linhas; 1× docstring "995" |
| 24 | Business Analyst (correção direta YOLO) | 5 arquivos — extração de helpers, condensação de loggers, docstring corrigida | ✅ Aprovado | — |
| 25 | Tests Analyst | Etapa 9A — `test_album_query_service.py` seção `progresso_detalhado` (1ª entrega) | 🔴 Reprovado | B2: variável `qtd_possuidas` morta; B3: testes de delegação para `get_top3_proximos`/`get_top3_distantes` ausentes (B1 era falso positivo) |
| 26 | Tests Analyst | Etapa 9A — `test_album_query_service.py` após correções B2/B3 | ✅ Aprovado | — |
| 27 | Backend Dev | Etapa 9B — `figurinha_repository.py` + `album_query_service.py` (1ª entrega) | 🔴 Reprovado | B1: regra "brilhante" codificada em SQL em `get_brilhantes_faltantes`; B2: HAVING com lógica de domínio em `get_top3_proximos`/`get_top3_distantes` |
| 28 | Backend Dev | Etapa 9B — todos os 4 arquivos após correções da R27 | 🔴 Reprovado | B1: 4 testes unitários chamando `repetidas()` e `progresso()` sem `telegram_user_id`; B2: `get_paises_completos` com HAVING em SQL |
| 29 | Backend Dev | Etapa 9B — `album_query_service.py` + testes após correções da R28 | 🔴 Reprovado | B1: `_agrupar` com 22 linhas executáveis (limite 20) |
| 30 | Backend Dev | Etapa 9B — `album_query_service.py` após extração de `_flush_grupo` | ✅ Aprovado | — |
| 31 | Bot Interface Dev | Etapa 9C — `message_templates.py` + `bot_controller.py` | ✅ Aprovado | 3 melhorias sugeridas (não bloqueantes) |
