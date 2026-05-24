# 🏆 Bot Figurinhas Copa 2026

Telegram bot para controle do álbum de figurinhas da Copa do Mundo 2026.
Cada usuário tem seu próprio álbum independente com as **994 figurinhas** oficiais.

> 🤖 **Acesse o bot no Telegram:** [@InformaFigurinhasBot](https://t.me/InformaFigurinhasBot)

---

## Funcionalidades

| Comando | Descrição |
|---|---|
| `/start` | Inicializa o álbum do usuário e exibe os comandos disponíveis |
| `/adicionar` | Adiciona figurinha ao estoque (fluxo conversacional) |
| `/adicionar_lote` | Adiciona várias figurinhas de uma vez (uma por linha) |
| `/remover` | Remove figurinha do estoque (fluxo conversacional) |
| `/progresso` | Exibe estatísticas detalhadas: percentual, países completos, top-3 próximos e distantes, brilhantes faltantes e CC faltantes |
| `/faltantes` | Lista figurinhas faltantes agrupadas por grupo de álbum (uma mensagem por grupo) |
| `/repetidas` | Lista figurinhas repetidas agrupadas por grupo de álbum (uma mensagem por grupo) |
| `/buscar` | Consulta o status de uma figurinha específica pelo código (fluxo conversacional) |
| `/buscar_pais` | Exibe o detalhamento completo de uma seleção: figurinhas que tem, repetidas (excedente para troca) e faltantes |
| `/consulta` | Exibe os dados armazenados sobre o usuário (Telegram ID, estatísticas do álbum e histórico de movimentações) |
| `/excluir_usuario` | Remove permanentemente todos os dados do usuário do banco de dados (fluxo conversacional com confirmação Sim/Não) |
| `/cancelar` | Cancela a operação em andamento |

### Formatos aceitos para códigos

O bot aceita múltiplos formatos de entrada:

```
BRA-1             → BRA-1
Brasil 1          → BRA-1
brasil-01         → BRA-1
Alemanha 5        → GER-5
Costa do Marfim 2 → CIV-2
FWC-0             → FWC-0
CC-14             → CC-14
```

---

## Estrutura do Álbum

- **12 grupos (A–L):** 4 seleções × 20 figurinhas = 960
- **FWC** (FIFA World Cup History): figurinhas 0–19 = 20 *(FWC-20 não existe no álbum físico)*
- **CC** (Coca-Cola): figurinhas 1–14 = 14
- **Total: 994 figurinhas**

### Figurinhas Brilhantes

São consideradas "brilhantes" a figurinha de **número 1** de cada seleção dos grupos A–L
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
  connection.py            ← ConnectionPool Singleton (search_path configurado via POSTGRES_SCHEMA)
  migrations/              ← 4 migrations SQL idempotentes
  homelab_init/            ← Script de inicialização do container Docker
seeds/                     ← album_data.py (fonte única de verdade) + script de seed
config/settings.py         ← Variáveis de ambiente com fail-fast
```

Princípios aplicados: **Clean Architecture**, **SOLID** (DIP via injeção de construtor),
**TDD** (testes escritos antes da implementação), **SRP** por camada.
Regras de negócio residem exclusivamente na camada de serviço — nunca em SQL.

---

## Deploy com Docker

> Para referência completa (backup, acesso direto ao banco, migração de dados),
> consulte [`docs/DEPLOY.md`](docs/DEPLOY.md).

### Pré-requisitos

| Requisito | Verificar com |
|---|---|
| Docker 24+ | `docker --version` |
| Docker Compose v2 | `docker compose version` |
| Git | `git --version` |

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd BotFigurinhas
```

### 2. Criar e preencher o `.env`

```bash
cp .env.example .env
```

Abra o `.env` e preencha **todos** os campos marcados com `<CHANGE_ME>`:

| Variável | O que preencher |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token obtido com o [@BotFather](https://t.me/BotFather) |
| `POSTGRES_DB` | Nome do banco de dados |
| `POSTGRES_USER` | Usuário de aplicação (role no PostgreSQL) |
| `POSTGRES_PASSWORD` | Senha do usuário de aplicação |
| `POSTGRES_SCHEMA` | Nome do schema onde as tabelas serão criadas |
| `POSTGRES_ADMIN_USER` | Superusuário interno do container PostgreSQL |
| `POSTGRES_ADMIN_PASSWORD` | Senha do superusuário do container |

> ⚠️ `POSTGRES_HOST` deve permanecer `db` ao rodar via Docker Compose — é o nome
> interno do serviço de banco de dados na rede do container.
>
> ⚠️ O arquivo `.env` está no `.gitignore` e **nunca deve ser commitado**.

### Como as credenciais fluem

```
.env
 ├── POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_SCHEMA
 │     ├── lidos pelo bot (config/settings.py) → pool de conexões
 │     └── repassados ao container do banco como POSTGRES_APP_USER /
 │           POSTGRES_APP_PASSWORD / POSTGRES_SCHEMA (via docker-compose.yml)
 │               └── usados pelo script database/homelab_init/00_setup.sh
 │                   para criar o role e o schema na primeira inicialização
 └── POSTGRES_ADMIN_USER / POSTGRES_ADMIN_PASSWORD
       └── usados pelo container PostgreSQL como superusuário interno
           (apenas na inicialização — nunca expostos ao bot)
```

### 3. Subir os containers

```bash
docker compose -f docker-compose.yml up -d --build
```

Na **primeira execução**, o PostgreSQL roda automaticamente
`database/homelab_init/00_setup.sh`, que:

1. Cria o role de aplicação definido em `POSTGRES_USER`
2. Cria o schema definido em `POSTGRES_SCHEMA` e transfere a propriedade
3. Aplica as 4 migrations SQL em sequência dentro do schema
4. Concede as permissões necessárias ao role de aplicação

Nas execuções seguintes o script é ignorado — o volume `pgdata` já existe
e os dados são preservados.

### 4. Verificar o status

```bash
# Ver se os dois containers estão rodando
docker compose ps

# Acompanhar os logs do banco (útil na primeira execução)
docker compose logs db

# Acompanhar os logs do bot
docker compose logs -f bot
```

O bot está pronto quando o log exibir `Application started`.

### 5. Atualizar para uma nova versão

```bash
git pull
docker compose -f docker-compose.yml up -d --build bot
```

O banco **não** é reinicializado — o volume `pgdata` persiste os dados entre atualizações.

---

## Desenvolvimento local

O `docker-compose.override.yml` ativa hot reload e expõe a porta do PostgreSQL
para acesso direto via cliente local (ex: DBeaver, psql):

```bash
docker compose up   # usa o override automaticamente
```

---

## Execução sem Docker

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
# Editar: POSTGRES_HOST=localhost e credenciais do seu banco local
```

### 3. Criar o schema e aplicar migrations

```bash
# Criar o schema manualmente no PostgreSQL
psql -h localhost -U <admin> -d <banco> \
  -c 'CREATE SCHEMA IF NOT EXISTS "AlbumCopa2026";'

# Aplicar as migrations dentro do schema
for f in 001 002 003 004; do
  PGOPTIONS='-c search_path="AlbumCopa2026"' \
    psql -h localhost -U <usuario> -d <banco> \
    -f database/migrations/${f}_*.sql
done
```

### 4. Iniciar o bot

```bash
python main.py
```

---

## Testes

```bash
# Configurar variáveis do banco de teste
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

| Variável | Obrigatória | Descrição |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Sim | Token do bot (obtido com o @BotFather) |
| `POSTGRES_HOST` | Sim | Host do banco (`db` em Docker, `localhost` sem Docker) |
| `POSTGRES_PORT` | Não | Porta PostgreSQL (padrão: `5432`) |
| `POSTGRES_DB` | Sim | Nome do banco de dados |
| `POSTGRES_USER` | Sim | Usuário de aplicação (role no PostgreSQL) |
| `POSTGRES_PASSWORD` | Sim | Senha do usuário de aplicação |
| `POSTGRES_SCHEMA` | Sim | Schema onde as tabelas são criadas |
| `POSTGRES_ADMIN_USER` | Sim¹ | Superusuário interno do container PostgreSQL |
| `POSTGRES_ADMIN_PASSWORD` | Sim¹ | Senha do superusuário do container |
| `DB_POOL_MIN` | Não | Conexões mínimas no pool (padrão: `1`) |
| `DB_POOL_MAX` | Não | Conexões máximas no pool (padrão: `10`) |

¹ Necessário apenas para o deploy com Docker. Não é usado pelo bot em execução.
