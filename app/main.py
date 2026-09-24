from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import IngestionPayload
from app.database import SessionLocal
from app.etl import run_etl_pipeline

app = FastAPI(
    title="E-Commerce ETL Pipeline API",
    description="API para ingestão de dados brutos, transformação em tempo real e carga no Data Lake e PostgreSQL.",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/ingest", status_code=status.HTTP_201_CREATED)
def ingest_data(payload: IngestionPayload, db: Session = Depends(get_db)):
    try:
        processed_count = run_etl_pipeline(payload.records, db)
        return {
            "status": "success",
            "message": f"Pipeline executado com sucesso. {processed_count} registos processados.",
            "processed_records": processed_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no processamento ETL: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy"}