# 🛒 E-Commerce ETL Pipeline API

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Enabled-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=flat-square&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=flat-square&logo=pandas)

🇬🇧 A high-performance REST API for e-commerce data ingestion, transformation, and loading using Medallion Architecture (Bronze, Silver, and Gold layers) in a Dockerized environment.

🇧🇷 Uma API de alta performance para ingestão, transformação e carga de dados de e-commerce utilizando a Arquitetura Medalhão (camadas Bronze, Prata e Ouro) em ambiente containerizado com Docker.

---

## 🏗️ Arquitetura do Projeto

O pipeline processa transações brutas via endpoints RESTful e aplica as etapas de ETL organizadas em três camadas:

1. **Camada Bronze (Raw Ingestion):** Recebe o payload JSON bruto via API e persiste os dados em seu formato imutável e original na pasta local (`data/bronze/`).
2. **Camada Silver (Cleaned & Structured):** Realiza a limpeza de texto (remoção de espaços e padronização em maiúsculas), faz a conversão de tipos de dados e persiste o resultado em formato colunar otimizado Parquet (`data/silver/`), além de carregar no banco **PostgreSQL** (`silver_processed_data`).
3. **Camada Gold (Business Aggregations & Analytics):** Processa e consolida as métricas de negócios (como total de vendas por categoria, ticket médio e volume por cliente), gerando tabelas prontas para consumo analítico e BI (`data/gold/` e PostgreSQL).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Framework Web:** FastAPI & Uvicorn
* **Manipulação de Dados:** Pandas & PyArrow (Parquet)
* **Banco de Dados:** PostgreSQL & SQLAlchemy ORM
* **Validação de Schemas:** Pydantic
* **Infraestrutura:** Docker & Docker Compose

---

## 📁 Estrutura do Repositório
````
.
├── app/
│   ├── main.py            # Endpoints FastAPI e rotas do pipeline
│   ├── database.py        # Conexão e sessão do PostgreSQL
│   ├── models.py          # Modelos SQLAlchemy (Tabelas do Banco)
│   └── schemas.py         # Schemas de validação Pydantic
├── data/
│   ├── bronze/            # Ingestão bruta (JSON)
│   ├── silver/            # Dados limpos e padronizados (Parquet)
│   └── gold/              # Dados agregados para analytics (Parquet)
├── docker-compose.yml     # Orquestração do PostgreSQL e FastAPI
├── Dockerfile             # Containerização da aplicação Python
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação técnica
````

---

## 🚀 Setup & Execution

### Pré-requisitos

* Docker Desktop instalado e em execução.
* Git instalado.

### Passo a Passo

1. **Clonar o repositório:**
```
git clone [https://github.com/evertonhenriquealves/ecommerce-etl-api.git](https://github.com/evertonhenriquealves/ecommerce-etl-api.git)
cd ecommerce-etl-api

```


2. **Subir os containers da aplicação e banco de dados:**
```
docker-compose up -d --build
```


3. **Acessar a documentação interativa da API:**
Abra o navegador e acesse:
* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`


---

## 🔌 Endpoints da API

* `POST /ingest` — Ingestão de novas transações (Gera arquivo Bronze, processa Silver e consolida Gold).
* `GET /data/silver` — Retorna os registros limpos da camada Silver.
* `GET /analytics/gold` — Retorna as métricas agregadas de negócios da camada Gold.

---

## 🔍 Consultas Rápidas no PostgreSQL

Comandos para consultar os dados inseridos diretamente no container do PostgreSQL:

* **Consultar registros limpos (Camada Silver):**
```
docker exec -it postgres_db psql -U user_admin -d db_ecommerce -c "SELECT * FROM silver_processed_data LIMIT 10;"

```

* **Consultar dados agregados (Camada Gold):**
```
docker exec -it postgres_db psql -U user_admin -d db_ecommerce -c "SELECT * FROM gold_aggregated_analytics;"
```
