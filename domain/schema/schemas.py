from pydantic import BaseModel
from typing import Annotated, List
from typing import TypedDict
import datetime

class TransactionRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    country: str
    channel: str
    device_id: str
    timestamp: datetime.datetime
    
class UsualBehavior(BaseModel):
    customer_id: str
    usual_amount_avg: float
    usual_hours: str  # Ejemplo: "08-20"
    usual_countries: str  # Ejemplo: "PE"
    usual_devices: str  # Ejemplo: "D-01"


class AgentState(TypedDict, total=False):
    transaction_request: TransactionRequest
    usual_behavior: UsualBehavior | None
    transaction_data: dict
    behavior_data: dict
    signals: List[str]
    rag_evidence: List[dict]  # Resultados RAG
    search_evidence: List[dict]  # Resultados Web Search
    debate_summary: str
    decision: str  # APPROVE, CHALLENGE, BLOCK, ESCALATE_TO_HUMAN
    confidence: float
    explanation_customer: str
    explanation_audit: str
    need_human_review: bool
    audit_trail: List[dict]  # Para trazabilidad
