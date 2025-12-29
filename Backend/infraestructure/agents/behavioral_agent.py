from domain.schema.schemas import AgentState
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import json

class BehavioralAgent:

    def __init__(self, llm):
        self.llm = llm
        self.name = "BehavioralAgent"

    async def analyze_behavior(self, state: AgentState) -> Dict[str, Any]:
        transaction = state["transaction_request"].dict()
        behavior = state["usual_behavior"].dict()
        context = state.get("anomaly_signals", {})
        agent_audit = state.get("agent_audit", [])
        
        # Extract hour from timestamp (handle both string and datetime objects)
        timestamp = transaction["timestamp"]
        if isinstance(timestamp, str):
            hour = datetime.fromisoformat(timestamp).hour
        else:
            hour = timestamp.hour
        
        # Create messages for the LLM
        system_message = SystemMessage(content="""Eres un experto en análisis de comportamiento financiero para el BCP.
            Analiza si esta transacción es consistente con el patrón histórico del cliente.
            Considera: monto, horario, ubicación, dispositivo.

            RESPONDE SIEMPRE EN JSON con la siguiente estructura:
            {
                "deviation_score": <número entre 0 y 1, donde 0 es comportamiento normal y 1 es muy desviado>,
                "notes": "<análisis conciso de la desviación>"
            }""")
                    
        user_content = f"""Cliente: {transaction["customer_id"]}
            Comportamiento habitual:
            - Monto promedio: {behavior["usual_amount_avg"]}
            - Horarios: {behavior["usual_hours"]}
            - Países: {behavior["usual_countries"]}
            - Dispositivos conocidos: {behavior["usual_devices"]}

            Transacción actual:
            - Monto: {transaction["amount"]}
            - Hora: {hour}:00
            - País: {transaction["country"]}
            - Dispositivo: {transaction["device_id"]}

            ¿Qué tan desviada está esta transacción del patrón normal? Responde en JSON."""
        
        user_message = HumanMessage(content=user_content)
        
        # Parse JSON response from LLM with retry
        max_retries = 3
        deviation_score = 0.5
        notes = ""
        
        for attempt in range(max_retries):
            try:
                response = await self.llm.ainvoke([system_message, user_message])
                content = response.content
                print("Behavioral Agent LLM Response:", content)
                
                # Extrae JSON desde el primer { hasta el último }
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx + 1]
                    llm_analysis = json.loads(json_str)
                    deviation_score = llm_analysis.get("deviation_score", 0.5)
                    notes = llm_analysis.get("notes", "")
                    break  # Success, exit retry loop
                else:
                    raise json.JSONDecodeError("No JSON found", content, 0)
                    
            except (json.JSONDecodeError, AttributeError, ValueError) as e:
                if attempt == max_retries - 1:
                    # Fallback after max retries
                    deviation_score = 0.5
                    notes = f"Error al parsear JSON después de {max_retries} intentos: {str(e)}"
        
        behavioral_analysis = {
            "pattern_deviation": notes,
            "deviation_score": deviation_score
        }
        
        # Agent decision tracking
        agent_decision = {
            "agent_name": "behavioral_agent",
            "status": "completed",
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "deviation_score": deviation_score
        }
        
        return {
            "behavioral_analysis": behavioral_analysis,
            "agent_audit": agent_audit + [agent_decision]
        }