# E-Commerce ETL Pipeline API

Uma API de alta performance para ingestão, transformação e carga de dados de e-commerce utilizando a **Medallion Architecture** (Bronze e Silver) em ambiente contêinerizado com Docker.

## 🏗️ Arquitetura do Projeto

O pipeline processa transações brutas via endpoints RESTful e aplica as etapas de ETL:

1. **Ingestão (Camada Bronze):** Recebe o payload JSON via API e persiste os dados em formato imutável na camada Bronze do Data Lake local (`data/bronze/`).
2. **Transformação (Camada Silver):** Limpa os dados de texto (remoção de espaços e padronização em maiúsculas), converte tipos de dados e persiste o resultado formatado em Parquet (`data/silver/`).
3. **Carga (Relacional):** Insere simultaneamente os dados estruturados na tabela `silver_processed_data` no **PostgreSQL**.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Framework Web:** FastAPI & Uvicorn
* **Manipulação de Dados:** Pandas & PyArrow (Parquet)
* **Banco de Dados:** PostgreSQL & SQLAlchemy ORM
* **Validação de Schemas:** Pydantic
* **Infraestrutura:** Docker & Docker Compose

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Docker Desktop instalado e em execução.

### Passo a Passo

1. Clone o repositório:
```bash
git clone [https://github.com/evertonhenriquealves/ecommerce-etl-api.git](https://github.com/evertonhenriquealves/ecommerce-etl-api.git)
cd ecommerce-etl-api