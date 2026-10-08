from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

class RawDataRecord(BaseModel):
    transaction_id: str = Field(min_length=1, description="Identificador único da transação")
    user_id: int
    product: str
    amount: float = Field(gt=0, description="O valor deve ser maior que zero")
    transaction_date: datetime

class IngestionPayload(BaseModel):
    records: List[RawDataRecord]
