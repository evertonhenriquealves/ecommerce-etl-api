# 🛒 E-Commerce ETL Pipeline API

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Enabled-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=flat-square&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=flat-square&logo=pandas)

🇬🇧 A REST API for e-commerce data ingestion, transformation, and loading using Medallion Architecture (Bronze, Silver, and Gold layers) in a Dockerized environment.

🇧🇷 Uma API REST para ingestão, transformação e carga de dados de e-commerce utilizando a Arquitetura Medalhão (camadas Bronze, Prata e Ouro) em ambiente containerizado com Docker.

---

## 🏗️ Arquitetura do Projeto

Cada chamada ao endpoint de ingestão recebe um lote de transações, valida o formato com o Pydantic e executa o pipeline em três camadas:

1. **Camada Bronze:** grava o lote recebido em JSON, sem nenhuma limpeza, em `data/bronze/vendas_<data_hora>.json`. Os dados já passaram pela validação de tipos da API, então a Bronze guarda o lote como foi aceito.
2. **Camada Silver:** remove espaços e converte o nome do produto para maiúsculas (coluna `product_clean`) e converte a data para `datetime`. O resultado é gravado em Parquet (`data/silver/vendas_limpas_<data_hora>.parquet`) e inserido na tabela `silver_processed_data` do PostgreSQL.
3. **Camada Gold:** agrega o lote por usuário (`total_spent`, `total_orders` e `last_transaction_date`). O lote agregado é gravado em Parquet (`data/gold/metricas_usuario_<data_hora>.parquet`), e os totais são somados aos já existentes na tabela `gold_user_metrics` do PostgreSQL.

```text
POST /api/v1/ingest
        │
        ▼
[ Validação Pydantic ] ──► [ Bronze: JSON ]
                                  │
                                  ▼
                       [ Silver: limpeza + Parquet + PostgreSQL ]
                                  │
                                  ▼
                       [ Gold: agregação por usuário + Parquet + PostgreSQL ]
```

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **API:** FastAPI e Uvicorn
* **Manipulação de dados:** Pandas e PyArrow (Parquet)
* **Banco de dados:** PostgreSQL 15 e SQLAlchemy
* **Validação:** Pydantic v2
* **Infraestrutura:** Docker e Docker Compose

---

## 📁 Estrutura do Repositório

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py            # Rotas da API (FastAPI)
│   ├── etl.py             # Pipeline Bronze, Silver e Gold
│   ├── database.py        # Conexão com o PostgreSQL e modelos das tabelas
│   └── schemas.py         # Esquemas de validação (Pydantic)
├── data/
│   ├── bronze/            # Lotes recebidos (JSON)
│   ├── silver/            # Dados limpos (Parquet)
│   └── gold/              # Métricas por usuário de cada lote (Parquet)
├── docker-compose.yml     # PostgreSQL e API
├── Dockerfile             # Imagem da aplicação
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar

**Pré-requisitos:** Docker Desktop em execução e Git instalado.

1. Clone o repositório:

```bash
git clone https://github.com/evertonhenriquealves/ecommerce-etl-api.git
cd ecommerce-etl-api
```

2. Suba os containers (a primeira vez demora mais, porque a imagem é construída):

```bash
docker-compose up -d --build
```

3. Abra a documentação interativa (Swagger), onde é possível testar as rotas:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

> As credenciais do banco (`etl_user` / `etl_password`) estão no `docker-compose.yml` e servem apenas para uso local e de estudo.

---

## 🔌 Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Verifica se a API está no ar |
| `POST` | `/api/v1/ingest` | Recebe um lote de transações e executa o pipeline (Bronze, Silver e Gold) |
| `GET` | `/api/v1/metrics/users` | Retorna as métricas acumuladas por usuário (camada Gold) |

**Exemplo de corpo para o `POST /api/v1/ingest`:**

```json
{
  "records": [
    {
      "user_id": 101,
      "product": "  teclado mecanico rgb  ",
      "amount": 350.5,
      "transaction_date": "2026-09-27T10:00:00"
    },
    {
      "user_id": 102,
      "product": "cabo hdmi 2.1 2m",
      "amount": 45.0,
      "transaction_date": "2026-09-27T11:00:00"
    }
  ]
}
```

Resposta esperada: `{"status": "success", "processed_records": 2}`. O campo `amount` deve ser maior que zero.

---

## 🔍 Consultas no PostgreSQL

Com os containers em execução, na pasta do projeto:

Inspeção de Amostra e Validação de Esquema — Camada Silver:
```bash
docker-compose exec db psql -U etl_user -d etl_db -c "SELECT * FROM silver_processed_data LIMIT 10;"
```

Validação de Métricas Agregadas e Regras de Negócio — Camada Gold:
```bash
docker-compose exec db psql -U etl_user -d etl_db -c "SELECT user_id, total_spent, total_orders FROM gold_user_metrics;"
```

---

### 📝 Note

🇬🇧 This is a study project. The data is synthetic, created to test the pipeline.

🇧🇷 Projeto de estudo. Os dados são sintéticos, criados para testar o pipeline.
