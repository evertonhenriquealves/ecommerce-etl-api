import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://etl_user:etl_password@db:5432/etl_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SilverProcessedData(Base):
    __tablename__ = "silver_processed_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_clean = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)