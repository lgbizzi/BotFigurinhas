# PROJECT_DEV.md — Album Copa 2026

> Arquivo de controle do projeto. Mantido e atualizado exclusivamente pelo **Business Analyst**.

---

## Status Geral

🟢 **Implementação completa** — Etapas 0 a 5 concluídas, aguardando revisão final (Etapa 6)

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

### Etapa 6 — Revisão Final e Testes de Integração Ponta a Ponta
> Agentes: **QA** + **Tests Analyst**

| # | Tarefa | Status | Observações |
|---|---|---|---|
| 6.1 | Testes de integração E2E dos fluxos /adicionar e /remover | ⬜ Pendente | |
| 6.2 | Revisão QA final — toda a codebase | ⬜ Pendente | |
| 6.3 | Validação de cobertura ≥ 90% (services + repositories) | ⬜ Pendente | |

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
