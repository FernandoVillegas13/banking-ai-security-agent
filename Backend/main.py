import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from infraestructure.langgraph_init import LangGraphInit
from infraestructure.openai_client import OpenAIClient
from infraestructure.redis_adapter import RedisAdapter
from infraestructure.aws.dynamo import DynamoService
from domain.schema.schemas import TransactionRequest, UsualBehavior, AgentState, HITLReviewRequest
from application.search_usual import SearchUsual
from datetime import datetime


# Inicializar adaptadores y servicios
app = FastAPI()
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Inicializar grafo
try:
    redis = RedisAdapter()
    search_usual = SearchUsual()
    dynamo_service = DynamoService()
    openai_client = OpenAIClient()
    llm = openai_client.get_llm()
    graph = LangGraphInit(llm, redis)
except Exception as e:
    print(f"Error inicializando grafo: {e}")
    graph = None


@app.post("/analize")
async def chat(request: TransactionRequest):
    try:
        print("-----"*25)
        # Conseguir comportamiento usual del cliente
        usual_behavior = search_usual.get_usual_behavior_by_customer_id(request.customer_id)

        # Crear estado inicial
        state = AgentState(
            transaction_id=request.transaction_id,
            transaction_request=request,
            usual_behavior=usual_behavior
        )

        if graph is None:
            return {"status": "error", "message": "Grafo no inicializado"}        
        result = await graph.runnable.ainvoke(input=state)
        
        try:
            dynamo_service.save_transaction(result)
        except Exception as e:
            print(f"Error guardando en DynamoDB: {str(e)}")
        
        return result
    
    except Exception as e:
        print("Error processing:", str(e))
        return {
            "status": "error", 
            "message": str(e)
        }

@app.get("/hitl/pending")
async def get_pending_hitl():
    try:
        pending_ids = redis.get_pending_hitl_transactions()
        queue_length = redis.get_hitl_queue_length()
        
        return {
            "status": "success",
            "queue_length": queue_length,
            "pending_transactions": pending_ids
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/hitl/{transaction_id}")
async def get_hitl_transaction(transaction_id: str):
    try:
        transaction_in_queue = redis.get_hitl_transaction(transaction_id)
        
        if not transaction_in_queue:
            return {
                "status": "error",
                "message": f"Transaction {transaction_id} not found in HITL queue"
            }
        
        transaction_data = dynamo_service.get_transaction(transaction_id)
        print("Transaction data retrieved:", transaction_data)
        
        return {
            "status": "success",
            "data": transaction_data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/hitl/{transaction_id}/review")
async def review_transaction(transaction_id: str, review: HITLReviewRequest):
    try:
        valid_decisions = ["APPROVE", "BLOCK"]
        if review.decision not in valid_decisions:
            return {
                "status": "error",
                "message": f"Invalid decision. Must be one of: {valid_decisions}"
            }
        
        success = redis.update_hitl_decision(
            transaction_id,
            review.decision,
            review.reviewer_notes
        )
        
        if not success:
            return {
                "status": "error",
                "message": f"Transaction {transaction_id} not found or already reviewed"
            }
        
        transaction_data = dynamo_service.get_transaction(transaction_id)
        
        if transaction_data:
            
            human_review_audit = {
                "agent_name": "human_review",
                "status": "completed",
                "execution_time": datetime.utcnow().isoformat() + 'Z',
                "decision": review.decision,
                "reviewer_notes": review.reviewer_notes
            }
            
            agent_audit = transaction_data.get('agent_audit', [])
            agent_audit.append(human_review_audit)
            
            updates = {
                'last_decision': {
                    'value': review.decision,
                    'decided_by': 'human',
                    'reviewer_notes': review.reviewer_notes,
                    'reviewed_at': datetime.utcnow().isoformat() + 'Z'
                },
                'agent_audit': agent_audit,
                'reviewed_by_human': True
            }
            
            dynamo_service.update_transaction(transaction_id, updates)
            print(f"Transaction {transaction_id} updated with human review")
        
        return {
            "status": "success",
            "message": f"Transaction {transaction_id} reviewed successfully",
            "decision": review.decision
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: str):
    try:
        transaction = dynamo_service.get_transaction(transaction_id)
        
        if not transaction:
            return {
                "status": "error",
                "message": f"Transaction {transaction_id} not found"
            }
        
        return {
            "status": "success",
            "data": transaction
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/transactions")
async def get_all_transactions(limit: Optional[int] = None):
    try:
        transactions = dynamo_service.get_all_transactions(limit=limit)
        
        return {
            "status": "success",
            "count": len(transactions),
            "data": transactions
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}