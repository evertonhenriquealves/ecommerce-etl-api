from pydantic import BaseModel, Field
from typing import List

class RawDataRecord(BaseModel):
    user_id: int
    product: str
    amount: float = Field(gt=0, description="O valor deve ser maior que zero")
    transaction_date: str

class IngestionPayload(BaseModel):
    records: List[RawDataRecord]