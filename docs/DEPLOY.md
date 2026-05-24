# Deploy — BotFigurinhas Copa 2026

Guia completo para colocar o bot em produção usando Docker Compose.

---

## Visão geral da arquitetura

```
┌─────────────────────────────────────────┐
│              Docker Compose             │
│                                         │
│   ┌─────────────┐   ┌────────────────┐  │
│   │   bot       │──▶│   db           │  │
│   │ (Python)    │   │ (PostgreSQL 16)│  │
│   └─────────────┘   └────────────────┘  │
│                             │            │
│                      volume: pgdata      │
└─────────────────────────────────────────┘
```

- **bot** — container Python que executa o Telegram bot (`main.py`)
- **db** — container PostgreSQL 16 com banco e schema definidos no `.env`
- **pgdata** — volume Docker que persiste os dados do banco entre reinicializações

---

## Pré-requisitos

| Requisito | Versão mínima | Verificar |
|---|---|---|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2 (plugin) | `docker compose version` |
| postgresql-client | qualquer | `pg_dump --version` *(só para migração)* |

---

## 1. Configuração inicial

### 1.1 Clonar o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repo>/projects/BotFigurinhas
```

### 1.2 Criar o arquivo `.env`

Copie o template e preencha os valores obrigatórios:

```bash
cp .env.example .env
```

Edite `.env` com as suas credenciais:

```dotenv
# Telegram — obtenha o token com o @BotFather
TELEGRAM_BOT_TOKEN=<CHANGE_ME>

# Banco de dados — credenciais de aplicação (usadas pelo bot)
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=<CHANGE_ME>
POSTGRES_USER=<CHANGE_ME>
POSTGRES_PASSWORD=<CHANGE_ME>
POSTGRES_SCHEMA=<CHANGE_ME>

# Banco de dados — superusuário interno do container
# Usado apenas na inicialização; nunca altere após o volume pgdata existir
POSTGRES_ADMIN_USER=<CHANGE_ME>
POSTGRES_ADMIN_PASSWORD=<CHANGE_ME>

# Pool de conexões
DB_POOL_MIN=1
DB_POOL_MAX=10
```

> **Atenção:** nunca commite o arquivo `.env` com credenciais reais.
> O `.gitignore` já exclui esse arquivo.

---

## 2. Inicialização do banco de dados

Na **primeira execução**, o PostgreSQL inicializa o banco e roda automaticamente
o script `database/homelab_init/00_setup.sh`, que:

1. Cria o role de aplicação definido em `POSTGRES_USER` com a senha configurada
2. Cria o schema definido em `POSTGRES_SCHEMA` e transfere a propriedade para o role
3. Aplica as migrations 001–004 em sequência dentro do schema
4. Concede todas as permissões necessárias ao role de aplicação

Esse processo ocorre uma única vez. Nas reinicializações seguintes, o PostgreSQL
ignora o diretório `docker-entrypoint-initdb.d/` porque o volume `pgdata` já existe.

---

## 3. Deploy em produção

Use **somente** o `docker-compose.yml` principal (sem o override de desenvolvimento):

```bash
docker compose -f docker-compose.yml up -d --build
```

### Verificar status

```bash
# Verificar se os containers estão rodando
docker compose ps

# Acompanhar logs do banco (inicialização)
docker compose logs db

# Acompanhar logs do bot
docker compose logs -f bot
```

O bot está pronto quando o log exibir algo como:

```
Application started
```

---

## 4. Migração de dados do banco anterior (informapromo)

Se você possui dados no banco `informapromo` e deseja migrá-los para o `homelab`,
execute o script após o container `db` estar saudável:

### 4.1 Pré-requisito

O `pg_dump` e o `psql` precisam estar instalados na **máquina host** (não dentro
do container):

```bash
# Ubuntu/Debian
sudo apt install postgresql-client

# macOS
brew install libpq
```

### 4.2 Preencher as variáveis de origem no `.env`

O script lê as variáveis com prefixo `SRC_` do arquivo `.env`:

```dotenv
SRC_POSTGRES_HOST=<CHANGE_ME>
SRC_POSTGRES_PORT=5432
SRC_POSTGRES_DB=<CHANGE_ME>
SRC_POSTGRES_USER=<CHANGE_ME>
SRC_POSTGRES_PASSWORD=<CHANGE_ME>
```

### 4.3 Executar o script

```bash
chmod +x database/migrate_from_informapromo.sh
./database/migrate_from_informapromo.sh
```

O script executa 4 passos:

| Passo | O que faz |
|---|---|
| 1 | `pg_dump` — exporta `figurinhas` e `movimentacoes` do informapromo |
| 2 | `sed` — substitui referências de schema `public` → `"AlbumCopa2026"` |
| 3 | `psql` — importa os dados no homelab |
| 4 | `SELECT` — valida contagem por usuário nas duas tabelas |

O arquivo de dump é salvo em `/tmp/informapromo_data_<timestamp>.sql` para
referência ou reexecução manual, se necessário.

---

## 5. Atualizações

Para atualizar o bot após mudanças no código:

```bash
git pull
docker compose -f docker-compose.yml up -d --build bot
```

O banco **não** é reinicializado — o volume `pgdata` persiste os dados.

---

## 6. Operações de manutenção

### Reiniciar apenas o bot

```bash
docker compose restart bot
```

### Ver logs em tempo real

```bash
docker compose logs -f bot
docker compose logs -f db
```

### Acessar o banco diretamente

```bash
docker compose exec db psql -U <POSTGRES_ADMIN_USER> -d <POSTGRES_DB> \
  -c "SET search_path TO \"<POSTGRES_SCHEMA>\";"
```

### Backup do banco

```bash
docker compose exec db pg_dump \
  -U <POSTGRES_ADMIN_USER> \
  -d <POSTGRES_DB> \
  -n '"<POSTGRES_SCHEMA>"' \
  --no-owner \
  -f /tmp/backup_$(date +%Y%m%d).sql

docker compose cp db:/tmp/backup_$(date +%Y%m%d).sql ./backups/
```

### Parar todos os serviços

```bash
docker compose down
```

> **Atenção:** `docker compose down -v` remove o volume `pgdata` e apaga todos
> os dados. Use com cuidado.

---

## 7. Estrutura de arquivos relevantes

```
projects/BotFigurinhas/
├── .env                          # Credenciais (não commitar)
├── .env.example                  # Template de credenciais
├── Dockerfile                    # Imagem do bot
├── docker-compose.yml            # Produção
├── docker-compose.override.yml   # Desenvolvimento local (hot reload + porta 5432)
├── database/
│   ├── connection.py             # Pool de conexões (lê POSTGRES_SCHEMA)
│   ├── homelab_init/
│   │   └── 00_setup.sh           # Init do container: role, schema, migrations
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_per_user_album.sql
│   │   ├── 003_add_pagina_to_figurinhas.sql
│   │   └── 004_update_pagina_values.sql
│   └── migrate_from_informapromo.sh  # Migração de dados do banco anterior
└── config/
    └── settings.py               # Lê variáveis de ambiente (inclui POSTGRES_SCHEMA)
```

---

## 8. Variáveis de ambiente — referência completa

| Variável | Obrigatória | Descrição |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Sim | Token do bot (obtido com o @BotFather) |
| `POSTGRES_HOST` | Sim | Host do banco (`db` em produção Docker) |
| `POSTGRES_PORT` | Não | Porta PostgreSQL (padrão: `5432`) |
| `POSTGRES_DB` | Sim | Nome do banco de dados |
| `POSTGRES_USER` | Sim | Usuário de aplicação (role no PostgreSQL) |
| `POSTGRES_PASSWORD` | Sim | Senha do usuário de aplicação |
| `POSTGRES_SCHEMA` | Sim | Schema onde as tabelas são criadas |
| `POSTGRES_ADMIN_USER` | Sim | Superusuário interno do container PostgreSQL |
| `POSTGRES_ADMIN_PASSWORD` | Sim | Senha do superusuário do container |
| `DB_POOL_MIN` | Não | Conexões mínimas no pool (padrão: `1`) |
| `DB_POOL_MAX` | Não | Conexões máximas no pool (padrão: `10`) |
| `SRC_POSTGRES_HOST` | Migração | Host do banco de origem (informapromo) |
| `SRC_POSTGRES_PORT` | Migração | Porta do banco de origem |
| `SRC_POSTGRES_DB` | Migração | Nome do banco de origem |
| `SRC_POSTGRES_USER` | Migração | Usuário do banco de origem |
| `SRC_POSTGRES_PASSWORD` | Migração | Senha do banco de origem |
