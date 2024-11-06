
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Location(BaseModel):
    latitude: float
    longitude: float

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    dateTime: datetime
    location: Optional[Location]
    transactionName: str
    transactionType: str

class Account(BaseModel):
    account_id: str
    name: str
    amount: float
    user_id: str
    transactions: List[Transaction] = []

class AnomalyResponse(BaseModel):
    is_anomaly: bool
    confidence: float
    reason: str
    transaction_id: str
    
class TransactionStatistics(BaseModel):
    income_median: Optional[float] = None
    income_min: Optional[float] = None
    income_max: Optional[float] = None
    income_count: Optional[int] = None
    expense_median: Optional[float] = None
    expense_min: Optional[float] = None
    expense_max: Optional[float] = None
    expense_count: Optional[int] = None

class AmountAnomalyResponse(BaseModel):
    is_anomaly: bool
    confidence: float
    reason: str
    transaction_id: str
    statistics: Optional[TransactionStatistics]