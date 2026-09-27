import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://etl_user:etl_password@db:5432/etl_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- CAMADA SILVER ---
class SilverDataModel(Base):
    __tablename__ = "silver_processed_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_clean = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)

# --- CAMADA GOLD ---
class GoldUserMetricsModel(Base):
    __tablename__ = "gold_user_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    total_spent = Column(Float, nullable=False)
    total_orders = Column(Integer, nullable=False)
    last_transaction_date = Column(DateTime, nullable=False)

# Para criação de todas as tabelas (Silver e Gold) no PostgreSQL se ainda não existirem:
Base.metadata.create_all(bind=engine)