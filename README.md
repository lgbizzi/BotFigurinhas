# 🏆 Bot Figurinhas Copa 2026

Telegram bot para controle do álbum de figurinhas da Copa do Mundo 2026. Cada usuário tem seu próprio álbum independente com as 995 figurinhas oficiais.

---

## Funcionalidades

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicializa o álbum do usuário e exibe os comandos disponíveis |
| `/adicionar` | Adiciona figurinha ao estoque (fluxo conversacional) |
| `/adicionar_lote` | Adiciona várias figurinhas de uma vez (uma por linha) |
| `/remover` | Remove figurinha do estoque (fluxo conversacional) |
| `/progresso` | Exibe % de completude do álbum |
| `/faltantes` | Lista figurinhas faltantes agrupadas por país |
| `/repetidas` | Lista figurinhas repetidas (quantidade > 1) |
| `/cancelar` | Cancela a operação em andamento |

### Formatos aceitos para códigos

O bot aceita múltiplos formatos de entrada:

```
BRA-1       → BRA-1
Brasil 1    → BRA-1
brasil-01   → BRA-1
Alemanha 5  → GER-5
Costa do Marfim 2 → CIV-2
FWC-0       → FWC-0
CC-14       → CC-14
```

---

## Estrutura do Álbum

- **12 grupos (A–L):** 4 seleções × 20 figurinhas = 960
- **FWC** (FIFA World Cup History): figurinhas 0–19 = 20
- **CC** (Coca-Cola): figurinhas 1–14 = 14
- **Total: 995 figurinhas**

---

## Stack

- **Runtime:** Python 3.12
- **Bot framework:** python-telegram-bot v22
- **Banco de dados:** PostgreSQL 16
- **Driver:** psycopg2 com ThreadedConnectionPool
- **Containerização:** Docker + docker-compose

---

## Arquitetura

```
bot/handlers/       ← Conversational handlers (PTB ConversationHandler)
controllers/        ← BotController: orquestra parser → service → templates
services/           ← FigurinhaService, AlbumQueryService, MovimentacaoService
repositories/       ← FigurinhaRepository, MovimentacaoRepository (todo SQL aqui)
models/             ← Dataclasses tipadas (Figurinha, Movimentacao, Progresso)
services/codigo_parser.py  ← Normalização pura de códigos (sem acesso a banco)
views/message_templates.py ← Todas as strings enviadas ao usuário
exceptions/         ← CodigoInvalidoError, FigurinhaNaoEncontradaError, etc.
database/           ← ConnectionPool Singleton + migrations SQL
seeds/              ← album_data.py (fonte única de verdade) + seed script
config/settings.py  ← Variáveis de ambiente com fail-fast
```

Princípios aplicados: **Clean Architecture**, **SOLID** (DIP via injeção de construtor), **TDD** (testes escritos antes da implementação), **SRP** por camada.

---

## Pré-requisitos

- Python 3.12+
- PostgreSQL 16+
- Token de bot do Telegram ([BotFather](https://t.me/BotFather))

---

## Configuração

### 1. Clonar e instalar dependências

```bash
git clone git@github.com:lgbizzi/BotFigurinhas.git
cd BotFigurinhas
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Editar `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nome_do_banco
POSTGRES_USER=usuario
POSTGRES_PASSWORD=senha

DB_POOL_MIN=1
DB_POOL_MAX=10
```

### 3. Criar o schema do banco

```bash
psql -h localhost -U <usuario> -d <banco> -f database/migrations/001_initial_schema.sql
```

### 4. Executar a migration de álbum por usuário

```bash
psql -h localhost -U <usuario> -d <banco> -f database/migrations/002_per_user_album.sql
```

### 5. Iniciar o bot

```bash
python main.py
```

O álbum de cada usuário é criado automaticamente no primeiro comando enviado.

---

## Docker

### Produção

```bash
cp .env.example .env   # preencher credenciais
docker compose up -d
```

### Desenvolvimento (hot reload)

```bash
docker compose up   # usa docker-compose.override.yml automaticamente
```

---

## Testes

```bash
# Configurar banco de teste
export POSTGRES_TEST_HOST=localhost
export POSTGRES_TEST_DB=album_copa_test
export POSTGRES_TEST_USER=postgres
export POSTGRES_TEST_PASSWORD=senha

pytest tests/ -v --cov
```

Estrutura dos testes:

```
tests/
├── conftest.py                          # Fixtures compartilhadas + isolamento por SAVEPOINT
├── unit/
│   ├── test_codigo_parser.py            # Todos os formatos e casos de erro do parser
│   ├── test_figurinha_service.py        # Service com mocks
│   └── test_movimentacao_service.py
└── integration/
    ├── test_figurinha_repository.py     # Contra banco real de teste
    ├── test_movimentacao_repository.py
    └── test_album_query_repository.py
```

---

## Migrations

| Arquivo | Descrição |
|---------|-----------|
| `001_initial_schema.sql` | Tabelas `figurinhas` e `movimentacoes`, índices e trigger de `updated_at` |
| `002_per_user_album.sql` | Adiciona `telegram_user_id` à tabela `figurinhas` para isolamento por usuário |
