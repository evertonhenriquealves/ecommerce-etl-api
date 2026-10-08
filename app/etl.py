import json
import os
from datetime import datetime

import pandas as pd
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal, SilverDataModel, GoldUserMetricsModel


def run_etl_pipeline(raw_records: list) -> dict:
    received = len(raw_records)
    if received == 0:
        return {"received": 0, "inserted": 0, "ignored": 0}

    # ------------------------------------------------------------------
    # 1. EXTRACT / INGESTION (Camada Bronze)
    # Guarda o lote exatamente como foi recebido, mesmo que tenha repetidos.
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

    # Se a mesma venda aparecer duas vezes no mesmo lote, fica só a primeira
    df = df.drop_duplicates(subset="transaction_id", keep="first")

    db = SessionLocal()
    try:
        # --------------------------------------------------------------
        # 3. LOAD SILVER (PostgreSQL)
        # Se o transaction_id já existe, o banco ignora a linha (sem erro).
        # O RETURNING devolve só os ids que realmente foram inseridos.
        # --------------------------------------------------------------
        silver_rows = [
            {
                "transaction_id": row["transaction_id"],
                "user_id": int(row["user_id"]),
                "product_clean": row["product_clean"],
                "amount": float(row["amount"]),
                "transaction_date": row["transaction_date"].to_pydatetime(),
            }
            for _, row in df.iterrows()
        ]

        silver_stmt = (
            insert(SilverDataModel)
            .values(silver_rows)
            .on_conflict_do_nothing(index_elements=["transaction_id"])
            .returning(SilverDataModel.transaction_id)
        )
        inserted_ids = [r[0] for r in db.execute(silver_stmt).fetchall()]

        gold_df = pd.DataFrame()

        if inserted_ids:
            # ----------------------------------------------------------
            # 4. GOLD: recalculada a partir da Silver (e não somada ao que já existia).
            # Assim o total sempre bate com o que a Silver contém.
            # ----------------------------------------------------------
            affected_users = [int(u) for u in df[df["transaction_id"].isin(inserted_ids)]["user_id"].unique()]

            aggregated = (
                db.query(
                    SilverDataModel.user_id.label("user_id"),
                    func.sum(SilverDataModel.amount).label("total_spent"),
                    func.count(SilverDataModel.id).label("total_orders"),
                    func.max(SilverDataModel.transaction_date).label("last_transaction_date"),
                )
                .filter(SilverDataModel.user_id.in_(affected_users))
                .group_by(SilverDataModel.user_id)
                .all()
            )

            gold_rows = [
                {
                    "user_id": a.user_id,
                    "total_spent": float(a.total_spent),
                    "total_orders": int(a.total_orders),
                    "last_transaction_date": a.last_transaction_date,
                }
                for a in aggregated
            ]

            gold_stmt = insert(GoldUserMetricsModel).values(gold_rows)
            gold_stmt = gold_stmt.on_conflict_do_update(
                index_elements=["user_id"],
                set_={
                    "total_spent": gold_stmt.excluded.total_spent,
                    "total_orders": gold_stmt.excluded.total_orders,
                    "last_transaction_date": gold_stmt.excluded.last_transaction_date,
                },
            )
            db.execute(gold_stmt)
            gold_df = pd.DataFrame(gold_rows)

        # Silver e Gold são confirmadas juntas: se algo falhar, nada fica pela metade
        db.commit()

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    # ------------------------------------------------------------------
    # 5. ARQUIVOS PARQUET (depois do commit, e só com o que foi novo)
    # ------------------------------------------------------------------
    if inserted_ids:
        os.makedirs("data/silver", exist_ok=True)
        df[df["transaction_id"].isin(inserted_ids)].to_parquet(
            f"data/silver/vendas_limpas_{timestamp}.parquet", index=False
        )

        os.makedirs("data/gold", exist_ok=True)
        gold_df.to_parquet(f"data/gold/metricas_usuario_{timestamp}.parquet", index=False)

    inserted = len(inserted_ids)
    return {"received": received, "inserted": inserted, "ignored": received - inserted}
