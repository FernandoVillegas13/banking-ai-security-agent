from domain.schema.schemas import AgentState
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from datetime import datetime
import json


class DecisionArbiter:
    def __init__(self, llm):
        self.llm = llm
    
    def _create_context_tool(self, state: AgentState):        
        @tool
        def obtener_contexto_total() -> str:
            """Obtiene y formatea el contexto para la decisión final."""
            tx_obj = state.get('transaction_request')
            bh_obj = state.get('usual_behavior')
            
            # Convertir objetos Pydantic a dict
            tx = tx_obj.model_dump() if tx_obj else {}
            bh = bh_obj.model_dump() if bh_obj else {}
            ba = state.get('behavioral_analysis', {})
            anom = state.get('anomaly_signals', {})
            sig = state.get('signals', [])
            rag = state.get('rag_evidence', [])
            web = state.get('search_evidence', [])
            deb = state.get('debate', [])
            
            ctx = f"""TRANSACCIÓN
                Monto: {tx.get('amount', 0)} {tx.get('currency', 'N/A')} | País: {tx.get('country', 'N/A')} | Dispositivo: {tx.get('device_id', 'N/A')}

                COMPORTAMIENTO HABITUAL
                Monto promedio: {bh.get('usual_amount_avg', 0)} | Horarios: {bh.get('usual_hours', 'N/A')} | Países: {bh.get('usual_countries', 'N/A')}

                DESVIACIÓN
                Score: {ba.get('deviation_score', 0)} | {ba.get('pattern_deviation', 'N/A')}

                ANOMALÍAS
                Señales: {', '.join(sig) if sig else 'Ninguna'}
                """
            
            for anom_type, data in anom.items():
                if isinstance(data, dict):
                    ctx += f"  {anom_type}: {data.get('is_anomaly', False)} (score: {data.get('score', 0):.2f})\n"
            
            if rag:
                ctx += "\nPOLÍTICAS INTERNAS\n"
                for ev in rag:
                    ctx += f"  {ev.get('policy_id', 'N/A')}: {ev.get('rule', 'N/A')} (sim: {ev.get('similarity_score', 0):.2f})\n"
            
            if web:
                ctx += "\nTHREAT INTELLIGENCE\n"
                for ev in web:
                    ctx += f"  {ev.get('fraud_type', 'N/A')}: {ev.get('summary', 'N/A')}\n"
            
            if deb:
                ctx += "\nDEBATE\n"
                for d in deb:
                    agent = "Pro-Customer" if d.get('agent') == 'pro_customer' else "Pro-Fraud"
                    ctx += f"  {agent}: {d.get('argument', 'N/A')}\n"
            
            print("Contexto:", ctx)
            return ctx
        
        return obtener_contexto_total
    
    async def decide(self, state: AgentState) -> Dict[str, Any]:
        start_time = datetime.now()
        context_tool = self._create_context_tool(state)
        llm_with_tools = self.llm.bind_tools([context_tool])
        
        system_prompt = """Eres árbitro de detección de fraude. Tu decisión DEBE basarse primariamente en las REGLAS INTERNAS.

        JERARQUÍA DE RELEVANCIA:
        1. REGLAS INTERNAS (POLÍTICAS) - Máxima prioridad pero cumpliendo sus criterios
        2. Anomalías detectadas - Confirmación de señales
        3. Evidencia externa (Threat Intelligence) - Contexto adicional
        4. Debate de agentes - Perspectivas adicionales

        DECISIONES: APPROVE | CHALLENGE | BLOCK | ESCALATE_TO_HUMAN

        CRITERIOS:
        - APPROVE: Unica anomalía leve o ninguna señal - Transaccion Legitima
        - CHALLENGE: Si se requieren validación adicional
        - BLOCK: Bloqueo si hay múltiples señales fuertes de fraude
        - ESCALATE_TO_HUMAN: Si es que cumple los criterios de la politica

        IMPORTANTE: Si una política interna aplica claramente, eso determina tu decisión.

        Responde SOLO con JSON:
        {"chain_of_thought": "razonamiento", "decision": "APPROVE|CHALLENGE|BLOCK|ESCALATE_TO_HUMAN", "confidence": 0.0-1.0}"""

        user_prompt = f"""Analiza y decide:

        Usa el tool 'obtener_contexto_total' para obtener el contexto.

        Responde con JSON válido (sin markdown):
        {{"chain_of_thought": "razonamiento", "decision": "APPROVE|CHALLENGE|BLOCK|ESCALATE_TO_HUMAN", "confidence": 0.0-1.0}}"""

        # Primera invocación - el LLM debería llamar al tool
        response1 = await llm_with_tools.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Verificar si hay tool calls
        if response1.tool_calls:
            tool_call = response1.tool_calls[0]
            contexto_completo = context_tool.invoke({})
            
            # Crear ToolMessage con el resultado
            tool_message = ToolMessage(
                content=contexto_completo,
                tool_call_id=tool_call['id']
            )
            
            response2 = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
                response1,
                tool_message,
                HumanMessage(content="Ahora responde con el JSON de decisión.")
            ])
            final_response = response2.content
        else:
            final_response = response1.content
        
        try:
            if "```json" in final_response:
                final_response = final_response.split("```json")[1].split("```")[0].strip()
            elif "```" in final_response:
                final_response = final_response.split("```")[1].split("```")[0].strip()
            
            decision_data = json.loads(final_response)
            decision = {
                "value": decision_data.get("decision", "ESCALATE_TO_HUMAN"),
                "chain_of_thought": decision_data.get("chain_of_thought", ""),
                "confidence": decision_data.get("confidence", 0.5)
            }
        except json.JSONDecodeError as e:
            decision = {
                "value": "ESCALATE_TO_HUMAN",
                "chain_of_thought": f"Error: {str(e)}",
                "confidence": 0.0
            }
        
        agent_audit = state.get('agent_audit', [])
        agent_audit.append({
            "agent_name": "decision_arbiter",
            "decision": decision['value'],
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": (datetime.now() - start_time).total_seconds()
        })
        
        return {
            "decision": decision,
            "agent_audit": agent_audit,
            "need_human_review": decision['value'] == "ESCALATE_TO_HUMAN"
        }
