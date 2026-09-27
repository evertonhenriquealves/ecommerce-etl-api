import json
import os
from datetime import datetime
import pandas as pd
from app.database import SessionLocal, SilverDataModel, GoldUserMetricsModel


def run_etl_pipeline(raw_records: list):
    # ------------------------------------------------------------------
    # 1. EXTRACT / INGESTION (Camada Bronze)
    # ------------------------------------------------------------------
    os.makedirs("data/bronze", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bronze_path = f"data/bronze/vendas_{timestamp}.json"
    
    with open(bronze_path, "w", encoding="utf-8") as f:
        json.dump(raw_records, f, indent=4, default=str)


    # ------------------------------------------------------------------
    # 2. TRANSFORM (Tratamento para Camada Silver)
    # ------------------------------------------------------------------
    df = pd.DataFrame(raw_records)
    df["product_clean"] = df["product"].astype(str).str.strip().str.upper()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])


    # ------------------------------------------------------------------
    # 3. LOAD SILVER (Data Lake Parquet & PostgreSQL)
    # ------------------------------------------------------------------
    os.makedirs("data/silver", exist_ok=True)
    silver_path = f"data/silver/vendas_limpas_{timestamp}.parquet"
    df.to_parquet(silver_path, index=False)

    db = SessionLocal()
    try:
        # Gravação na Silver (SQL)
        for _, row in df.iterrows():
            db_record = SilverDataModel(
                user_id=int(row["user_id"]),
                product_clean=row["product_clean"],
                amount=float(row["amount"]),
                transaction_date=row["transaction_date"]
            )
            db.add(db_record)
        db.commit()


        # --------------------------------------------------------------
        # 4. TRANSFORM & LOAD GOLD (Agregação de Métricas por Usuário)
        # --------------------------------------------------------------
        # Agrupa os dados do lote por usuário
        gold_df = df.groupby("user_id").agg(
            total_spent=("amount", "sum"),
            total_orders=("product_clean", "count"),
            last_transaction_date=("transaction_date", "max")
        ).reset_index()

        # Salva em Parquet na Camada Gold
        os.makedirs("data/gold", exist_ok=True)
        gold_path = f"data/gold/metricas_usuario_{timestamp}.parquet"
        gold_df.to_parquet(gold_path, index=False)

        # Gravação/Atualização na Gold (SQL - Lógica de Upsert)
        for _, row in gold_df.iterrows():
            uid = int(row["user_id"])
            existing_user = db.query(GoldUserMetricsModel).filter_by(user_id=uid).first()

            if existing_user:
                # Soma os novos valores aos totais acumulados
                existing_user.total_spent += float(row["total_spent"])
                existing_user.total_orders += int(row["total_orders"])
                if row["last_transaction_date"] > existing_user.last_transaction_date:
                    existing_user.last_transaction_date = row["last_transaction_date"]
            else:
                # Cria um novo registro para o usuário
                new_gold_record = GoldUserMetricsModel(
                    user_id=uid,
                    total_spent=float(row["total_spent"]),
                    total_orders=int(row["total_orders"]),
                    last_transaction_date=row["last_transaction_date"]
                )
                db.add(new_gold_record)

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    return len(df)