from fastapi import FastAPI, HTTPException, status
from app.schemas import IngestionPayload
from app.etl import run_etl_pipeline
from app.database import SessionLocal, GoldUserMetricsModel

app = FastAPI(
    title="E-Commerce ETL Pipeline API",
    description="API com Arquitetura Medalhão (Bronze, Silver e Gold) via FastAPI, Pandas e PostgreSQL."
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/ingest", status_code=status.HTTP_201_CREATED)
def ingest_data(payload: IngestionPayload):
    try:
        raw_data = [record.model_dump() for record in payload.records]
        result = run_etl_pipeline(raw_data)
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no processamento do pipeline ETL: {str(e)}"
        )

# --- CONSULTA DA CAMADA GOLD ---
@app.get("/api/v1/metrics/users")
def get_user_metrics():
    db = SessionLocal()
    try:
        metrics = db.query(GoldUserMetricsModel).all()
        return [
            {
                "user_id": m.user_id,
                "total_spent": round(m.total_spent, 2),
                "total_orders": m.total_orders,
                "last_transaction_date": m.last_transaction_date
            }
            for m in metrics
        ]
    finally:
        db.close()
