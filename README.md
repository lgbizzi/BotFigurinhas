# 🏆 Bot Figurinhas Copa 2026

Telegram bot para controle do álbum de figurinhas da Copa do Mundo 2026.
Cada usuário tem seu próprio álbum independente com as **994 figurinhas** oficiais.

---

## Funcionalidades

| Comando | Descrição |
|---|---|
| `/start` | Inicializa o álbum do usuário e exibe os comandos disponíveis |
| `/adicionar` | Adiciona figurinha ao estoque (fluxo conversacional) |
| `/adicionar_lote` | Adiciona várias figurinhas de uma vez (uma por linha) |
| `/remover` | Remove figurinha do estoque (fluxo conversacional) |
| `/progresso` | Exibe estatísticas detalhadas do álbum: percentual, países completos, top-3 próximos e distantes, brilhantes faltantes e CC faltantes |
| `/faltantes` | Lista figurinhas faltantes agrupadas por grupo de álbum (uma mensagem por grupo) |
| `/repetidas` | Lista figurinhas repetidas agrupadas por grupo de álbum (uma mensagem por grupo) |
| `/cancelar` | Cancela a operação em andamento |

### Formatos aceitos para códigos

O bot aceita múltiplos formatos de entrada:

```
BRA-1           → BRA-1
Brasil 1        → BRA-1
brasil-01       → BRA-1
Alemanha 5      → GER-5
Costa do Marfim 2 → CIV-2
FWC-0           → FWC-0
CC-14           → CC-14
```

---

## Estrutura do Álbum

- **12 grupos (A–L):** 4 seleções × 20 figurinhas = 960
- **FWC** (FIFA World Cup History): figurinhas 0–19 = 20 *(FWC-20 não existe no álbum físico)*
- **CC** (Coca-Cola): figurinhas 1–14 = 14
- **Total: 994 figurinhas**

### Figurinhas Brilhantes

São consideradas "brilhantes" a figurinha de **número 1** de cada seleção dos grupos A–L,
e **todas as figurinhas FWC**. O comando `/progresso` lista as brilhantes que ainda faltam.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Runtime | Python 3.12 |
| Bot framework | python-telegram-bot v22 |
| Banco de dados | PostgreSQL 16 |
| Driver | psycopg2 com `ThreadedConnectionPool` |
| Containerização | Docker + Docker Compose v2 |

---

## Arquitetura

```
bot/handlers/              ← ConversationHandlers (PTB)
controllers/               ← BotController: orquestra parser → service → templates
services/
  figurinha_service.py     ← Adicionar / remover figurinhas
  album_query_service.py   ← Consultas somente-leitura (progresso_detalhado, faltantes…)
  movimentacao_service.py  ← Registro de movimentações
  codigo_parser.py         ← Normalização de códigos (sem acesso a banco)
repositories/              ← Todo SQL está aqui (FigurinhaRepository, MovimentacaoRepository)
models/                    ← Dataclasses tipadas: Figurinha, Movimentacao, Progresso
views/message_templates.py ← Todas as strings enviadas ao usuário
exceptions/                ← CodigoInvalidoError, FigurinhaNaoEncontradaError, etc.
database/
  connection.py            ← ConnectionPool Singleton (schema configurável via search_path)
  migrations/              ← 4 migrations SQL idempotentes
  homelab_init/            ← Script de inicialização do container Docker
seeds/                     ← album_data.py (fonte única de verdade) + script de seed
config/settings.py         ← Variáveis de ambiente com fail-fast
```

Princípios aplicados: **Clean Architecture**, **SOLID** (DIP via injeção de construtor),
**TDD** (testes escritos antes da implementação), **SRP** por camada.
Regras de negócio residem exclusivamente na camada de serviço — nunca em SQL.

---

## Deploy com Docker (produção)

> Para um guia completo com seção de manutenção e migração de dados, consulte [`docs/DEPLOY.md`](docs/DEPLOY.md).

### Pré-requisitos

- Docker 24+
- Docker Compose v2 (`docker compose version`)

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd BotFigurinhas
```

### 2. Configurar o arquivo `.env`

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```dotenv
# Telegram
TELEGRAM_BOT_TOKEN=<token obtido com o @BotFather>

# Credenciais da aplicação (usadas pelo bot)
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=homelab
POSTGRES_USER=lg.admin
POSTGRES_PASSWORD=<senha-forte>
POSTGRES_SCHEMA=AlbumCopa2026

# Superusuário interno do container (usado apenas na inicialização)
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=<senha-forte>

# Pool de conexões
DB_POOL_MIN=1
DB_POOL_MAX=10
```

> ⚠️ `POSTGRES_HOST` deve ser `db` (nome do serviço no Docker Compose).
> O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.

### 3. Subir os containers

```bash
docker compose -f docker-compose.yml up -d --build
```

Na **primeira execução**, o PostgreSQL roda automaticamente o script
`database/homelab_init/00_setup.sh`, que:

1. Cria o role de aplicação `"lg.admin"`
2. Cria o schema `"AlbumCopa2026"` e transfere a propriedade
3. Aplica as 4 migrations em sequência dentro do schema
4. Concede as permissões necessárias ao role de aplicação

Nas execuções seguintes o script é ignorado (volume `pgdata` já existe).

### 4. Verificar o status

```bash
docker compose ps
docker compose logs -f bot
```

O bot está pronto quando o log exibir `Application started`.

### 5. Atualizações

```bash
git pull
docker compose -f docker-compose.yml up -d --build bot
```

---

## Desenvolvimento local

O `docker-compose.override.yml` ativa hot reload e expõe a porta do Postgres:

```bash
docker compose up   # usa o override automaticamente
```

---

## Configuração manual (sem Docker)

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
# Editar com POSTGRES_HOST=localhost e credenciais do seu banco local
```

### 3. Aplicar migrations

```bash
psql -h localhost -U <usuario> -d <banco> \
  -f database/migrations/001_initial_schema.sql \
  -f database/migrations/002_per_user_album.sql \
  -f database/migrations/003_add_pagina_to_figurinhas.sql \
  -f database/migrations/004_update_pagina_values.sql
```

### 4. Iniciar o bot

```bash
python main.py
```

---

## Testes

```bash
# Variáveis do banco de teste
export POSTGRES_TEST_HOST=localhost
export POSTGRES_TEST_DB=album_copa_test
export POSTGRES_TEST_USER=<usuario>
export POSTGRES_TEST_PASSWORD=<senha>

pytest tests/ -v --cov
```

Estrutura dos testes:

```
tests/
├── conftest.py                           # Fixtures + isolamento por SAVEPOINT
├── unit/
│   ├── test_codigo_parser.py             # Parser: todos os formatos e aliases
│   ├── test_album_query_service.py       # AlbumQueryService com mocks
│   ├── test_figurinha_service.py
│   └── test_movimentacao_service.py
└── integration/
    ├── test_figurinha_repository.py      # Contra banco real de teste
    ├── test_movimentacao_repository.py
    └── test_e2e_fluxos.py               # Fluxos completos: add/remove/query
```

---

## Migrations

| Arquivo | Descrição |
|---|---|
| `001_initial_schema.sql` | Tabelas `figurinhas` e `movimentacoes`, índices e trigger de `updated_at` |
| `002_per_user_album.sql` | Adiciona `telegram_user_id` para isolamento de álbum por usuário |
| `003_add_pagina_to_figurinhas.sql` | Adiciona coluna `pagina` (página física do álbum) |
| `004_update_pagina_values.sql` | Backfill de `pagina` para todas as figurinhas existentes |

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Sim | — | Token do bot (obtido com o @BotFather) |
| `POSTGRES_HOST` | Sim | — | Host do banco (`db` em produção Docker) |
| `POSTGRES_PORT` | Não | `5432` | Porta PostgreSQL |
| `POSTGRES_DB` | Sim | — | Nome do banco (`homelab`) |
| `POSTGRES_USER` | Sim | — | Usuário de aplicação (`lg.admin`) |
| `POSTGRES_PASSWORD` | Sim | — | Senha do usuário de aplicação |
| `POSTGRES_SCHEMA` | Sim | — | Schema do projeto (`AlbumCopa2026`) |
| `POSTGRES_ADMIN_USER` | Sim¹ | — | Superusuário do container (`postgres`) |
| `POSTGRES_ADMIN_PASSWORD` | Sim¹ | — | Senha do superusuário |
| `DB_POOL_MIN` | Não | `1` | Conexões mínimas no pool |
| `DB_POOL_MAX` | Não | `10` | Conexões máximas no pool |

¹ Necessário apenas para o deploy com Docker (inicialização do container).
