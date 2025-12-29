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


class DecisionResult(BaseModel):
    value: str  # APPROVE, CHALLENGE, BLOCK, ESCALATE_TO_HUMAN
    chain_of_thought: str  # Razonamiento del árbitro


class AgentState(TypedDict, total=False):
    transaction_id: str
    transaction_request: TransactionRequest
    usual_behavior: UsualBehavior | None
    behavioral_analysis: dict
    anomaly_score: float
    anomaly_signals: dict
    signals: List[str]
    rag_evidence: List[dict]  # Resultados RAG
    search_evidence: List[dict]  # Resultados Web Search
    debate: List[dict]  # Lista de argumentos del debate
    decision: dict  # {"value": str, "chain_of_thought": str}
    explanations: str
    explanation_audit: str
    agent_audit: List[dict]
    need_human_review: bool


class HITLReviewRequest(BaseModel):
    decision: str  # APPROVE, CHALLENGE, BLOCK
    reviewer_notes: str = ""