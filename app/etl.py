import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SilverProcessedData

# Garante que as pastas locais existem ao iniciar
os.makedirs("data/bronze", exist_ok=True)
os.makedirs("data/silver", exist_ok=True)

def run_etl_pipeline(raw_records: list, db: Session) -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # --- 1. CAMADA BRONZE (Extração) ---
    # Guarda o JSON bruto exatamente como chegou na API
    bronze_path = f"data/bronze/vendas_{timestamp}.json"
    with open(bronze_path, "w", encoding="utf-8") as f:
        json.dump([record.dict() for record in raw_records], f, ensure_ascii=False, indent=4)
        
    # --- 2. PROCESSAMENTO (Transformação) ---
    df = pd.DataFrame([record.dict() for record in raw_records])
    
    # Limpa espaços em branco e converte para maiúsculas
    df['product_clean'] = df['product'].str.strip().str.upper()
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # --- 3. CAMADA PRATA (Carga) ---
    # A) Guarda o dado tratado em formato Parquet no Data Lake
    silver_path = f"data/silver/vendas_limpas_{timestamp}.parquet"
    df.to_parquet(silver_path, index=False)
    
    # B) Guarda os mesmos dados na base de dados PostgreSQL
    records_to_insert = []
    for _, row in df.iterrows():
        records_to_insert.append(
            SilverProcessedData(
                user_id=row['user_id'],
                product_clean=row['product_clean'],
                amount=row['amount'],
                transaction_date=row['transaction_date']
            )
        )
    
    db.add_all(records_to_insert)
    db.commit()
    
    return len(records_to_insert)