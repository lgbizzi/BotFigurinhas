# Planejamento — Bot Telegram: Álbum de Figurinhas Copa do Mundo 2026

## Visão Geral do Projeto

Aplicação para controle de figurinhas do Álbum da Copa do Mundo 2026, com interface via Bot Telegram e persistência em banco de dados PostgreSQL. O sistema permitirá ao usuário registrar figurinhas obtidas, remover figurinhas trocadas e, futuramente, consultar o estado do álbum.

O bot precisa ficar em execução contínua para escutar os comandos enviados pelo usuário no Telegram. Por isso, toda a aplicação — bot Python e banco de dados PostgreSQL — é executada em containers Docker orquestrados por Docker Compose, garantindo portabilidade, isolamento e reinício automático em caso de falha.

---

## Estrutura do Álbum (Fonte: Planilha de Referência)

### Grupos e Seleções

| Grupo | Seleções |
|---|---|
| **A** | México (MEX), África do Sul (RSA), Coreia do Sul (KOR), República Tcheca (CZE) |
| **B** | Canadá (CAN), Bósnia e Herzegovina (BIH), Catar (QAT), Suíça (SUI) |
| **C** | Brasil (BRA), Marrocos (MAR), Haiti (HAI), Escócia (SCO) |
| **D** | Estados Unidos (USA), Paraguai (PAR), Austrália (AUS), Turquia (TUR) |
| **E** | Alemanha (GER), Curaçao (CUW), Costa do Marfim (CIV), Equador (ECU) |
| **F** | Holanda (NED), Japão (JPN), Suécia (SWE), Tunísia (TUN) |
| **G** | Bélgica (BEL), Egito (EGY), Irã (IRN), Nova Zelândia (NZL) |
| **H** | Espanha (ESP), Cabo Verde (CPV), Arábia Saudita (KSA), Uruguai (URU) |
| **I** | França (FRA), Senegal (SEN), Iraque (IRQ), Noruega (NOR) |
| **J** | Argentina (ARG), Argélia (ALG), Áustria (AUT), Jordânia (JOR) |
| **K** | Portugal (POR), RD Congo (COD), Uzbequistão (UZB), Colômbia (COL) |
| **L** | Inglaterra (ENG), Croácia (CRO), Gana (GHA), Panamá (PAN) |

### Contagem Total de Figurinhas

| Seção | Quantidade |
|---|---|
| Grupos A–L (12 grupos × 4 seleções × 20 figurinhas) | 960 |
| FIFA World Cup History — FWC 00, FWC 1 a FWC 19 | 21 |
| Coca-Cola — CC1 a CC14 | 14 |
| **Total** | **995** |

> **Nota sobre FWC:** a figurinha `FWC 00` corresponde à Página Inicial (capa), seguida de `FWC 1` a `FWC 19`, totalizando 20 figurinhas numeradas + 1 de capa = 21 figurinhas FWC.

---

## Resolução de Código da Figurinha (Parsing)

O sistema deve aceitar múltiplos formatos de entrada para identificar a mesma figurinha, normalizando-os internamente para o formato canônico `CODIGO-NUMERO` (ex: `BRA-1`).

### Formatos aceitos (exemplos para a mesma figurinha)

| Entrada do usuário | Resultado normalizado |
|---|---|
| `BRA-1` | `BRA-1` |
| `BRA 1` | `BRA-1` |
| `BRA01` | `BRA-1` |
| `BRA 01` | `BRA-1` |
| `BRA-01` | `BRA-1` |
| `Brasil 1` | `BRA-1` |
| `brasil 1` | `BRA-1` *(case-insensitive)* |
| `BRASIL-01` | `BRA-1` |

### Regras de normalização

1. **Conversão para maiúsculas** antes de qualquer processamento.
2. **Resolução de nome completo → código:** se a entrada começar com o nome completo de uma seleção (ex: `Brasil`, `Alemanha`, `Estados Unidos`), substituir pelo código oficial (ex: `BRA`, `GER`, `USA`). O mapeamento `nome → código` deve cobrir variações com e sem acentos (ex: `Franca` → `FRA`, `França` → `FRA`).
3. **Extração do número:** após isolar o código da seleção, extrair os dígitos finais, remover zeros à esquerda e converter para inteiro.
4. **Validação final:** verificar se o par `(codigo_selecao, numero)` existe na tabela `figurinhas`. Caso não exista, retornar erro descritivo.

### Casos especiais

- `FWC 00`, `FWC00`, `FWC-00` → figurinha de capa, número `0`
- `CC1`, `CC 1`, `CC-1`, `Coca-Cola 1` → `CC-1`
- Entradas ambíguas (ex: número fora do intervalo válido) devem retornar mensagem de erro clara

### Responsabilidade no código

O parsing ficará em um módulo dedicado:

```
services/
└── codigo_parser.py    # Normalização e resolução de aliases de códigos de figurinha
```

Este módulo será a **única** porta de entrada para resolução de códigos, consumido pelos handlers antes de chamar qualquer service de negócio. Deve conter o mapeamento completo `nome_completo → codigo_oficial` de todas as 48 seleções + FWC + CC.

---

## Modelo de Dados

### Tabela: `figurinhas`

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Identificador interno |
| `grupo` | `VARCHAR(3)` | Grupo do álbum (A–L, FWC, CC) |
| `codigo_selecao` | `VARCHAR(5)` | Código oficial da seleção (ex: MEX, BRA, FWC, CC) |
| `nome_selecao` | `VARCHAR(60)` | Nome completo (ex: México, Brasil, FIFA World Cup History) |
| `numero` | `SMALLINT` | Número da figurinha dentro da seleção (0 para FWC 00) |
| `codigo_figurinha` | `VARCHAR(10) UNIQUE NOT NULL` | Código canônico composto (ex: `BRA-1`, `FWC-0`, `CC-3`) |
| `quantidade` | `SMALLINT NOT NULL DEFAULT 0` | Quantidade em posse |
| `created_at` | `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` | Data de criação do registro |
| `updated_at` | `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` | Data da última atualização |

**Índice único:** `codigo_figurinha` (já garantido pelo `UNIQUE`).  
**Índice secundário:** `(codigo_selecao, numero)` para buscas por par.

---

### Tabela: `movimentacoes`

Registro de auditoria de todas as operações de entrada e saída.

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Identificador interno |
| `figurinha_id` | `INTEGER NOT NULL REFERENCES figurinhas(id)` | Referência à figurinha |
| `tipo` | `VARCHAR(10) NOT NULL` | `ENTRADA` ou `SAIDA` |
| `quantidade` | `SMALLINT NOT NULL` | Quantidade movimentada (sempre positivo) |
| `origem` | `VARCHAR(20) NOT NULL DEFAULT 'MANUAL'` | `MANUAL`, `TROCA` (para uso futuro) |
| `observacao` | `TEXT` | Campo livre para anotações |
| `telegram_user_id` | `BIGINT` | ID do usuário Telegram que realizou a operação |
| `telegram_username` | `VARCHAR(100)` | Username do usuário Telegram |
| `entrada_bruta` | `VARCHAR(100)` | Texto original digitado pelo usuário (para debug) |
| `created_at` | `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` | Timestamp da operação |

> **Nota:** a coluna `entrada_bruta` registra exatamente o que o usuário digitou antes do parsing, útil para auditoria e melhoria futura do parser.

---

## Infraestrutura Docker

O bot precisa rodar de forma contínua para escutar comandos no Telegram (modelo de long polling). Isso exige que o processo Python fique ativo indefinidamente, o que torna o uso de containers Docker obrigatório.

### Serviços Docker Compose

A stack é composta por dois serviços:

| Serviço | Imagem base | Responsabilidade |
|---|---|---|
| `bot` | `python:3.12-slim` | Executa o `main.py` em loop contínuo (long polling do Telegram) |
| `db` | `postgres:16-alpine` | Banco de dados PostgreSQL com volume persistente |

### Arquivos Docker

```
album_copa_2026/
├── Dockerfile                   # Imagem do serviço bot (Python)
├── docker-compose.yml           # Orquestração: bot + db (produção/uso local)
├── docker-compose.override.yml  # Overrides para desenvolvimento local (ex: volume de código para hot-reload)
└── .env                         # Variáveis reais (nunca versionado — listado no .gitignore)
    .env.example                 # Template de variáveis sem valores sensíveis (versionado)
```

### Especificação do `Dockerfile`

- Imagem base: `python:3.12-slim`
- Instalar dependências do `requirements.txt`
- Copiar o código da aplicação
- Definir `CMD ["python", "main.py"]`
- Rodar como usuário não-root (segurança)
- Não copiar arquivos de teste, `.env` ou `__pycache__` (via `.dockerignore`)

### Especificação do `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:          # lidos de variáveis de ambiente / arquivo .env
      POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    volumes:
      - pgdata:/var/lib/postgresql/data          # persistência dos dados
      - ./database/migrations:/docker-entrypoint-initdb.d  # executa DDL na criação
    healthcheck:
      test: pg_isready -U ${POSTGRES_USER}
      interval: 5s
      retries: 5

  bot:
    build: .
    restart: always
    env_file: .env
    depends_on:
      db:
        condition: service_healthy    # aguarda o banco estar pronto antes de subir

volumes:
  pgdata:
```

### Especificação do `docker-compose.override.yml`

Usado apenas em desenvolvimento local. Monta o código como volume para permitir edição sem rebuild:

```yaml
services:
  bot:
    volumes:
      - .:/app          # hot-reload manual (reiniciar o container para refletir mudanças)
    command: ["python", "-u", "main.py"]   # output sem buffer para logs legíveis
```

### Fluxo de inicialização em produção

```
docker compose up -d
    ↓
db sobe e executa 001_initial_schema.sql automaticamente (initdb.d)
    ↓
healthcheck confirma que o PostgreSQL está pronto
    ↓
bot sobe, conecta ao banco via variáveis de ambiente
    ↓
main.py verifica se o seed já foi executado; se não, executa
    ↓
bot inicia polling e fica escutando comandos do Telegram
```

### Seed em ambiente Docker

O `seed_figurinhas.py` pode ser executado de duas formas:

1. **Automaticamente pelo `main.py`** na primeira inicialização (verificando se `figurinhas` está vazia)
2. **Manualmente via `docker compose exec`:** `docker compose exec bot python seeds/seed_figurinhas.py`

### Observações de segurança

- O arquivo `.env` com valores reais **nunca é versionado** (incluído no `.gitignore`)
- O `.env.example` documenta todas as variáveis sem valores sensíveis e **é versionado**
- O container `bot` roda com usuário não-root
- A porta do PostgreSQL **não é exposta** para o host em produção (comunicação apenas pela rede interna Docker)

---

## Arquitetura — Padrão MVC + SOLID + Clean Code

```
album_copa_2026/
│
├── Dockerfile                           # Imagem do serviço bot
├── docker-compose.yml                   # Orquestração: bot + db
├── docker-compose.override.yml          # Overrides para desenvolvimento local
├── .dockerignore                        # Exclui testes, .env, __pycache__ da imagem
│
├── main.py                              # Entrypoint: inicializa banco e sobe o bot
│
├── config/
│   └── settings.py                      # Leitura de variáveis de ambiente (.env)
│
├── database/
│   ├── connection.py                    # Pool de conexões PostgreSQL
│   └── migrations/
│       └── 001_initial_schema.sql       # DDL: figurinhas + movimentacoes
│
├── models/
│   ├── figurinha.py                     # Dataclass da entidade Figurinha
│   └── movimentacao.py                 # Dataclass da entidade Movimentacao
│
├── repositories/
│   ├── base_repository.py               # ABC genérica de repositório
│   ├── figurinha_repository.py          # find_by_codigo, find_by_par, update_quantidade
│   └── movimentacao_repository.py       # insert
│
├── services/
│   ├── codigo_parser.py                 # Normalização e resolução de aliases de entrada
│   ├── figurinha_service.py             # Regras de negócio: adicionar, remover
│   └── movimentacao_service.py          # Orquestração do registro de movimentações
│
├── controllers/
│   └── bot_controller.py                # Orquestra: parser → service → view → resposta
│
├── views/
│   └── message_templates.py             # Formatação de todas as mensagens do bot
│
├── bot/
│   ├── handlers/
│   │   ├── adicionar_handler.py         # ConversationHandler do /adicionar
│   │   └── remover_handler.py           # ConversationHandler do /remover
│   └── bot_setup.py                     # Registro de todos os handlers na Application
│
├── seeds/
│   ├── album_data.py                    # Definição estruturada de todos os grupos/seleções
│   └── seed_figurinhas.py               # Script de carga inicial no banco
│
├── exceptions/
│   └── domain_exceptions.py             # FigurinhaNaoEncontradaError, QuantidadeInsuficienteError, CodigoInvalidoError
│
├── tests/
│   ├── unit/
│   │   ├── test_codigo_parser.py        # Testa todos os formatos e aliases aceitos
│   │   ├── test_figurinha_service.py
│   │   └── test_movimentacao_service.py
│   └── integration/
│       └── test_figurinha_repository.py
│
├── requirements.txt
├── .env.example                         # Template de variáveis (versionado)
├── .gitignore                           # Inclui .env, __pycache__, volumes Docker
└── README.md
```

---

## Fluxos do Bot

### Comando `/adicionar`

1. Usuário envia `/adicionar`
2. Bot solicita: *"Qual o código da figurinha? (ex: BRA-1, Brasil 1, MEX 05)"*
3. Usuário informa o código em qualquer formato aceito
4. `CodigoParser.normalizar()` resolve o input → código canônico
   - Se inválido: bot informa o erro e solicita novamente (sem sair do fluxo)
5. Bot exibe a figurinha identificada e solicita a quantidade a adicionar
6. Usuário informa a quantidade (inteiro positivo)
7. `BotController` chama `FigurinhaService.adicionar(codigo_canonico, quantidade, user_info, entrada_bruta)`
8. Service incrementa `quantidade` no banco → `MovimentacaoService.registrar()` grava o log
9. Bot responde com confirmação: nome da figurinha + novo saldo

### Comando `/remover`

1. Usuário envia `/remover`
2. Bot solicita o código da figurinha (mesmo fluxo de parsing do `/adicionar`)
3. `CodigoParser.normalizar()` resolve o input
   - Se inválido: bot informa o erro e solicita novamente
4. Bot exibe a figurinha e o saldo atual, solicita a quantidade a remover
5. Usuário informa a quantidade
6. `BotController` chama `FigurinhaService.remover(codigo_canonico, quantidade, user_info, entrada_bruta)`
7. Service valida: `quantidade_atual >= quantidade_a_remover`
   - Se insuficiente: bot informa saldo atual e solicita quantidade menor
8. Service decrementa `quantidade` → `MovimentacaoService.registrar()` grava o log
9. Bot responde com confirmação: nome da figurinha + novo saldo

### Validações Comuns

- Código resolvido deve existir na tabela `figurinhas`
- Quantidade informada deve ser inteiro positivo (≥ 1)
- Remoção não pode resultar em quantidade negativa
- Todos os erros retornam mensagem amigável sem encerrar o fluxo desnecessariamente

---

## Tecnologias e Dependências

### Aplicação Python

| Biblioteca | Versão | Finalidade |
|---|---|---|
| `python-telegram-bot` | ≥ 20.x | Framework do Bot Telegram (async) |
| `psycopg2-binary` | ≥ 2.9 | Driver PostgreSQL |
| `python-dotenv` | ≥ 1.0 | Gerenciamento de variáveis de ambiente |
| `pydantic` | ≥ 2.x | Validação de modelos/DTOs |
| `pytest` | ≥ 8.x | Framework de testes |
| `pytest-asyncio` | ≥ 0.23 | Suporte a testes assíncronos |
| `unidecode` | ≥ 1.3 | Normalização de acentos no parser de códigos |

### Infraestrutura

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Docker | ≥ 24.x | Containerização dos serviços |
| Docker Compose | ≥ 2.x | Orquestração local da stack (bot + db) |
| PostgreSQL | 16 (Alpine) | Banco de dados relacional |
| Python | 3.12 (Slim) | Runtime da aplicação |

---

## Princípios de Design Aplicados

### Single Responsibility (SRP)
Cada camada tem uma única responsabilidade: `CodigoParser` só normaliza entradas, `Repository` só acessa dados, `Service` só contém regras de negócio, `Handler` só interpreta o contexto do Telegram, `View` só formata mensagens.

### Open/Closed (OCP)
`BaseRepository` define o contrato. Novos repositórios estendem sem alterar a base. Novos handlers e formatos de código são adicionados sem modificar os módulos existentes.

### Liskov Substitution (LSP)
Repositórios concretos implementam a interface base e são intercambiáveis (facilita mocks em testes).

### Interface Segregation (ISP)
Interfaces específicas por domínio (figurinha, movimentação). Nenhum módulo depende de métodos que não utiliza.

### Dependency Inversion (DIP)
Services dependem de abstrações (interfaces de repositório), não de implementações concretas. Injeção de dependência via construtores.

### Clean Code
- Funções pequenas e com nome descritivo
- Sem comentários redundantes (código auto-documentado)
- Constantes nomeadas — sem magic numbers/strings
- Tratamento explícito de erros com exceções tipadas em `exceptions/domain_exceptions.py`
- Cobertura de testes unitários e de integração

---

## Etapas de Desenvolvimento

### Etapa 0 — Infraestrutura Docker
- [ ] Criar `Dockerfile` da aplicação Python
- [ ] Criar `docker-compose.yml` com serviços `bot` e `db`
- [ ] Criar `docker-compose.override.yml` para desenvolvimento local
- [ ] Criar `.dockerignore`
- [ ] Criar `.gitignore` (incluindo `.env`, `__pycache__`, volumes)
- [ ] Criar `.env.example` com todas as variáveis documentadas

### Etapa 1 — Infraestrutura e Banco de Dados
- [ ] Configurar `.env.example` com todas as variáveis necessárias
- [ ] Implementar `config/settings.py` com leitura via `python-dotenv`
- [ ] Implementar `database/connection.py` com pool de conexões
- [ ] Criar `001_initial_schema.sql` com as tabelas `figurinhas` e `movimentacoes`
- [ ] Implementar `seeds/album_data.py` com a estrutura completa do álbum (todos os grupos, seleções e códigos)
- [ ] Implementar `seeds/seed_figurinhas.py` para popular as 995 figurinhas no banco

### Etapa 2 — Parser de Códigos
- [ ] Implementar `services/codigo_parser.py` com mapeamento completo de nomes → códigos para todas as 48 seleções + FWC + CC
- [ ] Cobrir variações: case-insensitive, com/sem acento, com/sem separador, com/sem zero à esquerda
- [ ] Implementar testes unitários exaustivos em `tests/unit/test_codigo_parser.py` cobrindo todos os formatos da especificação e casos de borda

### Etapa 3 — Camada de Dados (Models + Repositories)
- [ ] Definir dataclasses `Figurinha` e `Movimentacao` em `models/`
- [ ] Implementar `BaseRepository` com interface genérica (ABC)
- [ ] Implementar `FigurinhaRepository`: `find_by_codigo`, `find_by_par`, `update_quantidade`
- [ ] Implementar `MovimentacaoRepository`: `insert`
- [ ] Implementar testes de integração para `FigurinhaRepository`

### Etapa 4 — Camada de Negócio (Services + Exceptions)
- [ ] Definir exceções de domínio em `exceptions/domain_exceptions.py`: `FigurinhaNaoEncontradaError`, `QuantidadeInsuficienteError`, `CodigoInvalidoError`
- [ ] Implementar `FigurinhaService.adicionar()`
- [ ] Implementar `FigurinhaService.remover()`
- [ ] Implementar `MovimentacaoService.registrar()`
- [ ] Implementar testes unitários para os services (mockar repositórios)

### Etapa 5 — Camada de Apresentação (Bot + Views)
- [ ] Implementar `views/message_templates.py` com todas as mensagens formatadas
- [ ] Implementar `controllers/bot_controller.py` orquestrando parser → service → view
- [ ] Implementar `bot/handlers/adicionar_handler.py` com `ConversationHandler`
- [ ] Implementar `bot/handlers/remover_handler.py` com `ConversationHandler`
- [ ] Implementar `bot/bot_setup.py` registrando todos os handlers
- [ ] Implementar `main.py` inicializando banco e bot

### Etapa 6 — Testes de Integração do Bot
- [ ] Testes de ponta a ponta dos fluxos `/adicionar` e `/remover` com banco de teste

### Etapa 7 — Funções de Consulta (Backlog Futuro)
- [ ] `/status` — resumo geral (total de figurinhas/obtidas/faltando/repetidas)
- [ ] `/repetidas` — listar figurinhas com quantidade > 1
- [ ] `/faltando` — listar figurinhas com quantidade = 0, por grupo
- [ ] `/troca` — registrar troca entre duas figurinhas (SAIDA + ENTRADA atomicamente)
- [ ] `/historico` — exibir últimas N movimentações do usuário

---

## Observações para o Claude Code

- O módulo `seeds/album_data.py` deve ser a **fonte única de verdade** sobre a estrutura do álbum. O seed, o parser e qualquer futura funcionalidade de consulta devem referenciar este módulo, nunca duplicar os dados.
- O `CodigoParser` deve usar `unidecode` para normalizar acentos antes de comparar nomes, garantindo que `Franca` e `França` resolvam para `FRA`.
- O `ConversationHandler` do PTB deve ser usado para os fluxos multi-etapa, garantindo estado por usuário. Usar `states` bem definidos por handler.
- Todas as operações de banco devem estar em blocos `try/except` com rollback explícito de transações.
- O arquivo `.env.example` deve documentar todas as variáveis sem expor valores reais. O token do bot nunca deve aparecer no código-fonte nem na imagem Docker.
- O campo `entrada_bruta` na tabela `movimentacoes` é valioso para analisar padrões de uso e evoluir o parser ao longo do projeto.
- O campo `telegram_user_id` na tabela `movimentacoes` possibilitará, futuramente, controle multiusuário sem necessidade de migração de schema.
- O `docker-compose.yml` deve usar `depends_on` com `condition: service_healthy` para garantir que o bot só inicia após o PostgreSQL estar pronto para aceitar conexões.
- O migration SQL (`001_initial_schema.sql`) deve ser montado em `/docker-entrypoint-initdb.d/` no container do banco, garantindo execução automática na primeira inicialização.
- O `main.py` deve verificar se a tabela `figurinhas` está vazia antes de subir o bot; se estiver, executar o seed automaticamente. Isso garante que um `docker compose up` do zero suba tudo funcional sem passos manuais adicionais.
- A porta do PostgreSQL não deve ser exposta para o host em produção — apenas os containers da stack Docker se comunicam entre si pela rede interna.
