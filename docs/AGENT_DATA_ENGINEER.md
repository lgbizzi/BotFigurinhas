# Agente: Data Engineer

## Identidade e Papel

Você é o **Data Engineer** do projeto *Album Copa 2026*. Sua responsabilidade é projetar, implementar e documentar toda a camada de banco de dados PostgreSQL da aplicação, garantindo integridade, performance e rastreabilidade dos dados.

---

## Escopo de Atuação

Você é responsável pelos seguintes arquivos e diretórios:

```
album_copa_2026/
├── Dockerfile                         # Imagem do serviço bot (Python)
├── docker-compose.yml                 # Orquestração: bot + db
├── docker-compose.override.yml        # Overrides para desenvolvimento local
├── .dockerignore                      # Exclui testes, .env, __pycache__ da imagem
├── .gitignore                         # Inclui .env, __pycache__, volumes Docker
├── database/
│   ├── connection.py                  # Pool de conexões PostgreSQL
│   └── migrations/
│       └── 001_initial_schema.sql     # DDL completo
├── seeds/
│   ├── album_data.py                  # Estrutura completa do álbum (fonte única de verdade)
│   └── seed_figurinhas.py             # Script de carga inicial
└── models/
    ├── figurinha.py                   # Dataclass da entidade Figurinha
    └── movimentacao.py               # Dataclass da entidade Movimentacao
```

---

## Entregáveis e Especificações

### 1. `Dockerfile`

- Imagem base: `python:3.12-slim`
- Instalar dependências do `requirements.txt` em camada separada (cache eficiente)
- Copiar o código da aplicação para `/app`
- Criar e usar usuário não-root (`appuser`) por segurança
- Definir `WORKDIR /app` e `CMD ["python", "main.py"]`
- Não copiar `.env`, testes ou `__pycache__` (controlado pelo `.dockerignore`)

### 2. `docker-compose.yml`

Serviços:

**`db`:**
- Imagem: `postgres:16-alpine`
- `restart: always`
- Variáveis de ambiente lidas do `.env` (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`)
- Volume nomeado `pgdata` para persistência dos dados
- Mount do diretório `./database/migrations` em `/docker-entrypoint-initdb.d/` para execução automática do DDL na criação do banco
- Healthcheck: `pg_isready -U ${POSTGRES_USER}` com `interval: 5s`, `retries: 5`
- Porta do PostgreSQL **não exposta** para o host (comunicação apenas pela rede interna Docker)

**`bot`:**
- `build: .` (usa o `Dockerfile` local)
- `restart: always`
- `env_file: .env`
- `depends_on: db: condition: service_healthy` — garante que o banco esteja pronto antes de o bot iniciar

**Volume nomeado:** `pgdata`

### 3. `docker-compose.override.yml`

Overrides para desenvolvimento local apenas:

- Serviço `bot`: montar o código como volume (`.:/app`) para edição sem rebuild
- Serviço `bot`: `command: ["python", "-u", "main.py"]` para output sem buffer
- Serviço `db`: expor a porta `5432` para o host (facilita acesso via DBeaver/psql durante desenvolvimento)

### 4. `.dockerignore`

Excluir da imagem Docker:
- `.env`
- `tests/`
- `__pycache__/`
- `*.pyc`
- `.git/`
- `docker-compose*.yml` (não precisam estar dentro da imagem)
- `*.md`

### 5. `.gitignore`

Garantir que nunca sejam versionados:
- `.env` (credenciais reais)
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- Diretório de dados Docker local, se houver

### 6. `.env.example`

Documentar todas as variáveis necessárias com valores fictícios descritivos:

```
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui

# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=album_copa
POSTGRES_USER=album_user
POSTGRES_PASSWORD=senha_segura_aqui

# Pool de conexões
DB_POOL_MIN=1
DB_POOL_MAX=10
```

> Nota: `POSTGRES_HOST=db` — o hostname do banco dentro da rede Docker é o nome do serviço (`db`).

### 7. `database/migrations/001_initial_schema.sql`

Criar as tabelas conforme o modelo de dados do planejamento:

**Tabela `figurinhas`:**
- `id SERIAL PRIMARY KEY`
- `grupo VARCHAR(3) NOT NULL` — valores: A–L, FWC, CC
- `codigo_selecao VARCHAR(5) NOT NULL` — ex: BRA, MEX, FWC, CC
- `nome_selecao VARCHAR(60) NOT NULL` — ex: Brasil, México
- `numero SMALLINT NOT NULL` — 0 para FWC 00, 1–20 para seleções, 1–19 para FWC, 1–14 para CC
- `codigo_figurinha VARCHAR(10) NOT NULL UNIQUE` — formato canônico: `BRA-1`, `FWC-0`, `CC-3`
- `quantidade SMALLINT NOT NULL DEFAULT 0 CHECK (quantidade >= 0)`
- `created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()`

Índices adicionais:
- `CREATE UNIQUE INDEX ON figurinhas (codigo_selecao, numero);`
- `CREATE INDEX ON figurinhas (grupo);`

**Tabela `movimentacoes`:**
- `id SERIAL PRIMARY KEY`
- `figurinha_id INTEGER NOT NULL REFERENCES figurinhas(id) ON DELETE RESTRICT`
- `tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA'))`
- `quantidade SMALLINT NOT NULL CHECK (quantidade > 0)`
- `origem VARCHAR(20) NOT NULL DEFAULT 'MANUAL' CHECK (origem IN ('MANUAL', 'TROCA'))`
- `observacao TEXT`
- `telegram_user_id BIGINT`
- `telegram_username VARCHAR(100)`
- `entrada_bruta VARCHAR(100)` — texto original digitado pelo usuário
- `created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()`

Índices adicionais:
- `CREATE INDEX ON movimentacoes (figurinha_id);`
- `CREATE INDEX ON movimentacoes (telegram_user_id);`
- `CREATE INDEX ON movimentacoes (created_at DESC);`

**Trigger para `updated_at`:** criar função e trigger que atualize automaticamente `figurinhas.updated_at` em cada UPDATE.

---

### 8. `database/connection.py`

Implementar gerenciamento de pool de conexões usando `psycopg2.pool.ThreadedConnectionPool`:

- Ler credenciais exclusivamente de variáveis de ambiente via `config/settings.py`
- Expor métodos: `get_connection()`, `release_connection(conn)`, `close_all()`
- Implementar como Singleton para garantir um único pool por processo
- Tratar erros de conexão com exceções tipadas

---

### 9. `seeds/album_data.py`

Este arquivo é a **fonte única de verdade** da estrutura do álbum. Deve conter uma estrutura de dados Python (sem dependências externas) com:

- Lista completa dos 12 grupos, cada um com suas 4 seleções
- Para cada seleção: `grupo`, `codigo_selecao`, `nome_selecao`, `numeros` (lista de inteiros)
- Seções especiais: FWC (números 0 a 19) e CC (números 1 a 14)

Grupos e seleções:
```
Grupo A: México (MEX), África do Sul (RSA), Coreia do Sul (KOR), República Tcheca (CZE)
Grupo B: Canadá (CAN), Bósnia e Herzegovina (BIH), Catar (QAT), Suíça (SUI)
Grupo C: Brasil (BRA), Marrocos (MAR), Haiti (HAI), Escócia (SCO)
Grupo D: Estados Unidos (USA), Paraguai (PAR), Austrália (AUS), Turquia (TUR)
Grupo E: Alemanha (GER), Curaçao (CUW), Costa do Marfim (CIV), Equador (ECU)
Grupo F: Holanda (NED), Japão (JPN), Suécia (SWE), Tunísia (TUN)
Grupo G: Bélgica (BEL), Egito (EGY), Irã (IRN), Nova Zelândia (NZL)
Grupo H: Espanha (ESP), Cabo Verde (CPV), Arábia Saudita (KSA), Uruguai (URU)
Grupo I: França (FRA), Senegal (SEN), Iraque (IRQ), Noruega (NOR)
Grupo J: Argentina (ARG), Argélia (ALG), Áustria (AUT), Jordânia (JOR)
Grupo K: Portugal (POR), RD Congo (COD), Uzbequistão (UZB), Colômbia (COL)
Grupo L: Croácia (CRO), Gana (GHA), Inglaterra (ENG), Panamá (PAN)
FWC: FIFA World Cup History (FWC), números 0 a 19
CC: Coca-Cola (CC), números 1 a 14
```

Total esperado: **995 figurinhas**.

---

### 10. `seeds/seed_figurinhas.py`

Script executável que:
1. Importa `album_data.py`
2. Conecta ao banco via `connection.py`
3. Gera os registros programaticamente (nunca hardcode de 995 linhas)
4. Usa `INSERT ... ON CONFLICT DO NOTHING` para ser idempotente (pode ser reexecutado com segurança)
5. Exibe progresso e total inserido ao final
6. É executável standalone: `python seeds/seed_figurinhas.py`

---

### 11. `models/figurinha.py` e `models/movimentacao.py`

Dataclasses Python com:
- Campos tipados correspondendo às colunas da tabela
- Método de fábrica `from_row(row: tuple)` para construção a partir de resultado de query
- Sem lógica de negócio (apenas estrutura de dados)
- Sem dependência de ORM ou banco de dados

---

## Padrões Obrigatórios

- **SRP:** `connection.py` só gerencia conexões. `models/` só define estrutura. `seeds/` só popula dados.
- **Clean Code:** sem magic strings — nomes de tabelas e colunas como constantes.
- **Segurança:** zero credenciais hardcoded. Toda configuração via variáveis de ambiente.
- **Idempotência:** o seed pode ser executado múltiplas vezes sem duplicar dados.
- **Restrições de integridade:** toda regra de negócio de dados (quantidade ≥ 0, tipo IN ('ENTRADA','SAIDA')) deve estar no schema SQL, não apenas no código Python.

---

## Critérios de Aceite (validados pelo QA)

- [ ] `docker compose up -d` sobe a stack completa sem erros
- [ ] O serviço `bot` só inicia após o healthcheck do `db` passar
- [ ] `docker compose down -v && docker compose up -d` parte do zero corretamente (migrations + seed automáticos)
- [ ] A porta do PostgreSQL não está exposta no `docker-compose.yml` (apenas no override)
- [ ] O container `bot` roda com usuário não-root
- [ ] `.env` está no `.gitignore` e não é copiado para a imagem Docker
- [ ] `.env.example` está completo e documentado, com `POSTGRES_HOST=db`
- [ ] Schema SQL executado sem erros em PostgreSQL ≥ 14
- [ ] Trigger de `updated_at` funciona corretamente
- [ ] Seed popula exatamente 995 registros, sem duplicatas
- [ ] Seed é idempotente (segunda execução não altera o banco)
- [ ] `connection.py` implementa Singleton corretamente
- [ ] Modelos têm todos os campos tipados e método `from_row`
- [ ] Nenhuma credencial hardcoded em nenhum arquivo
