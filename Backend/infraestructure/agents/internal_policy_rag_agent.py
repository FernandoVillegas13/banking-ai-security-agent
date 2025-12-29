from domain.schema.schemas import AgentState
from datetime import datetime
from typing import Dict, Any, List
from qdrant_client import QdrantClient
from openai import OpenAI
import os

class InternalPolicyRAGAgent:
    
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.collection_name = "fraud_policies"
        self.qdrant_client = QdrantClient(url=self.qdrant_url)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.top_k = 2  # Número de políticas a recuperar

    def get_embedding(self, text: str) -> List[float]:
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding

    def build_search_query(self, state: AgentState) -> str:
        signals = state.get('signals', [])
        transaction = state['transaction_request']
        
        query = f"Fraud policy for {transaction.amount} {transaction.currency} in {transaction.country}. Anomalies: {', '.join(signals)}"
        return query

    async def search_policies(self, query: str) -> List[dict]:
        try:
            print(f"[RAG] Starting policy search with query: {query}")
            
            # Generar embedding de la query
            query_embedding = self.get_embedding(query)
            print(f"[RAG] Embedding generated, size: {len(query_embedding)}")
            
            # Buscar en Qdrant
            print(f"[RAG] Searching in Qdrant collection: {self.collection_name}")
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=self.top_k
            ).points
            print(f"[RAG] Found {len(results)} results from Qdrant")
            
            # Formatear resultados
            policies = []
            for idx, result in enumerate(results):
                policy = {
                    "rank": idx + 1,
                    "chunk_id": result.payload.get("chunk_id"),
                    "policy_id": result.payload.get("policy_id"),
                    "rule": result.payload.get("rule"),
                    "version": result.payload.get("version"),
                    "text": result.payload.get("text"),
                    "similarity_score": round(result.score, 4),
                    "retrieved_at": datetime.utcnow().isoformat() + "Z",
                }
                policies.append(policy)
                print(f"[RAG] Policy {idx + 1}: {policy['policy_id']} (score: {policy['similarity_score']})")
            
            print(f"[RAG] Search completed successfully with {len(policies)} policies")
            return policies
        
        except Exception as e:
            return [{
                "error": True,
                "message": f"Failed to retrieve policies: {str(e)}",
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
            }]

    async def get_policies(self, state: AgentState) -> Dict[str, Any]:
        # Construir query de búsqueda
        search_query = self.build_search_query(state)
        
        # Buscar políticas en Qdrant
        policies = await self.search_policies(search_query)
        
        # Crear audit entry simple
        agent_decision = {
            "agent_name": "internal_policy_rag_agent",
            "status": "completed",
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "search_query": search_query,
        }
        
        # Actualizar estado
        return {
            "rag_evidence": policies,
            "agent_audit": state.get('agent_audit', []) + [agent_decision],
        }
