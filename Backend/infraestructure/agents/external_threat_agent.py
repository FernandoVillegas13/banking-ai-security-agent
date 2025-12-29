
from perplexity import Perplexity
from typing import Dict, Any
from datetime import datetime
from langchain_core.tools import tool
import os

class ExternalThreatAgent():
    def __init__(self, llm):
        self.perplexityapikey = os.getenv("PERPLEXITY_API_KEY")
        self.llm = llm

    async def get_external_threat(self, state: Dict[str, Any]) -> Dict[str, Any]:
        transaction = state.get('transaction_request')
        search_evidence = []
        
        print(f"[SEARCH] Iniciando búsqueda de amenazas para transacción: {transaction.transaction_id}")
        
        # Crear tool para búsqueda
        @tool
        def search_external_threats(query: str) -> str:
            """Busca amenazas de fraude externas usando Perplexity API."""
            print(f"[SEARCH] Ejecutando búsqueda: {query}")
            client = Perplexity(api_key=self.perplexityapikey)
            
            try:
                prompt = f"""Busca información reciente sobre fraudes financieros relacionados con: {query}
                Identifica los 3 casos más relevantes con:
                - URL de la fuente
                - Descripción breve del fraude (100-150 caracteres)
                - Tipo de fraude"""

                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="sonar-pro",
                    web_search_options={"search_recency_filter": "week"},
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "threats": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "url": {"type": "string"},
                                                "summary": {"type": "string"},
                                                "fraud_type": {"type": "string"}
                                            },
                                            "required": ["url", "summary"]
                                        }
                                    }
                                },
                                "required": ["threats"]
                            }
                        }
                    }
                )
                
                import json
                content = completion.choices[0].message.content
                result = json.loads(content)
                
                retrieved_at = datetime.utcnow().isoformat() + "Z"
                threats = result.get('threats', [])
                                
                if threats:
                    for threat in threats[:3]:
                        search_evidence.append({
                            "url": threat.get('url', 'unknown'),
                            "summary": threat.get('summary', 'Sin descripción'),
                            "fraud_type": threat.get('fraud_type', 'N/A'),
                            "retrieved_at": retrieved_at
                        })
                else:
                    search_evidence.append({
                        "url": "perplexity_search",
                        "summary": "No se encontraron amenazas relevantes en la última semana",
                        "retrieved_at": retrieved_at
                    })
                
                return f"Encontradas {len(threats)} amenazas. Primera: {threats[0].get('summary', 'N/A')[:100] if threats else 'Ninguna'}"
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                search_evidence.append({
                    "url": "error",
                    "summary": error_msg,
                    "retrieved_at": datetime.utcnow().isoformat() + "Z"
                })
                return error_msg
        
        # ReAct agent simple: bind tool al LLM
        llm_with_tools = self.llm.bind_tools([search_external_threats])
        
        # Construir query basada en anomaly_signals
        anomalies = state.get('anomaly_signals', {})
        anomaly_types = []
        
        if anomalies.get('device_anomaly', {}).get('is_anomaly'):
            anomaly_types.append("dispositivos nuevos/desconocidos")
        if anomalies.get('time_anomaly', {}).get('is_anomaly'):
            anomaly_types.append("transacciones en horas inusuales")
        if anomalies.get('amount_anomaly', {}).get('is_anomaly'):
            anomaly_types.append(f"montos anómalos en {transaction.currency}")
            
        if anomaly_types:
            anomaly_str = ", ".join(anomaly_types)
            query = f"Fraudes recientes en {transaction.country} con patrones de: {anomaly_str}"
        else:
            query = f"Fraudes financieros recientes en {transaction.country}"
            
        messages = [{"role": "user", "content": query}]
        
        print(f"[SEARCH] Invocando ReAct agent")
        
        # Loop ReAct simple (1 iteración)
        response = await llm_with_tools.ainvoke(messages)
        
        # Si el LLM quiere llamar el tool
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'search_external_threats':
                    # Ejecutar el tool
                    tool_result = search_external_threats.invoke(tool_call['args'])
                    print(f"[SEARCH] Tool ejecutado: {tool_result[:100]}...")    
        
        # Agent decision tracking
        agent_decision = {
            "agent_name": "external_threat_agent",
            "status": "completed",
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "query_used": query
        }
        
        agent_audit = state.get('agent_audit', [])
        agent_audit.append(agent_decision)
        
        return {
            "search_evidence": search_evidence,
            "agent_audit": agent_audit
        }    
