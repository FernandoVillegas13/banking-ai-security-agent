from domain.schema.schemas import AgentState
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import json
from time import time


class DebateAgent():
    def __init__(self, llm):
        self.llm = llm

    async def debate(self, state: AgentState) -> Dict[str, Any]:
        start_time = datetime.now()
        anomaly_signals = state.get('anomaly_signals', {})
        signals = state.get('signals', [])
        transaction_request = state.get('transaction_request', {})
        behavioral_analysis = state.get('behavioral_analysis', {})
        agent_audit = state.get('agent_audit', [])
        
        # Pro-customer system message
        pro_customer_system = """Eres un agente defensor del cliente. Tu rol es argumentar que la transacción es legítima y que las señales anómalas tienen explicaciones razonables. Sé breve y conciso (máximo 2-3 oraciones)."""
        # Pro-fraud system message
        pro_fraud_system = """Eres un agente detector de fraude. Tu rol es argumentar que las señales anómalas son preocupantes y sugieren riesgo de fraude. Sé breve y conciso (máximo 2-3 oraciones)."""
        
        debate_transcript = []
        context_summary = self._build_context_summary(anomaly_signals, signals, transaction_request, behavioral_analysis)
        
        for round_num in range(1, 3):
            # Pro-customer argument
            customer_prompt = f"""Round {round_num}/3
                Contexto de la transacción:
                {context_summary}
                {"Debate previo: " + json.dumps(debate_transcript, indent=2, ensure_ascii=False) if debate_transcript else ""}
                Argumenta brevemente por qué esta transacción podría ser legítima."""

            customer_response = await self.llm.ainvoke([
                SystemMessage(content=pro_customer_system),
                HumanMessage(content=customer_prompt)
            ])
            
            customer_arg = customer_response.content
            debate_transcript.append({
                "round": round_num,
                "agent": "pro_customer",
                "argument": customer_arg,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # Pro-fraud argument
            fraud_prompt = f"""Round {round_num}/3
                Contexto de la transacción:
                {context_summary}
                Argumento del defensor del cliente:
                {customer_arg}
                {"Debate previo: " + json.dumps(debate_transcript[:-1], indent=2, ensure_ascii=False) if len(debate_transcript) > 1 else ""}
                Rebate brevemente argumentando el riesgo de fraude."""

            fraud_response = await self.llm.ainvoke([
                SystemMessage(content=pro_fraud_system),
                HumanMessage(content=fraud_prompt)
            ])
            
            fraud_arg = fraud_response.content
            debate_transcript.append({
                "round": round_num,
                "agent": "pro_fraud",
                "argument": fraud_arg,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        
        # Register audit trail
        num_rounds = len([t for t in debate_transcript if t["agent"] == "pro_fraud"])
        agent_audit.append({
            "agent_name": "debate_agents",
            "rounds": num_rounds,
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": (datetime.now() - start_time).total_seconds()
        })
        
        # Update confidence based on debate        
        return {
            "debate": debate_transcript,
            "agent_audit": agent_audit,
        }
    
    def _build_context_summary(self, anomaly_signals: Dict, signals: list, transaction_request, behavioral_analysis: Dict) -> str:
        summary_parts = []
        
        # Transaction basics
        if transaction_request:
            amount = transaction_request.amount if hasattr(transaction_request, 'amount') else transaction_request.get('amount', 0)
            currency = transaction_request.currency if hasattr(transaction_request, 'currency') else transaction_request.get('currency', 'PEN')
            country = transaction_request.country if hasattr(transaction_request, 'country') else transaction_request.get('country', 'N/A')
            summary_parts.append(f"Transacción: {amount} {currency} en {country}")
        
        # Anomaly signals
        if anomaly_signals:
            summary_parts.append("\nSeñales de anomalía:")
            
            amount_anom = anomaly_signals.get('amount_anomaly', {})
            if amount_anom:
                summary_parts.append(f"- Monto: {amount_anom.get('reason', 'N/A')} (score: {amount_anom.get('score', 0):.2f})")
            
            time_anom = anomaly_signals.get('time_anomaly', {})
            if time_anom:
                summary_parts.append(f"- Horario: {time_anom.get('reason', 'N/A')} (score: {time_anom.get('score', 0):.2f})")
            
            device_anom = anomaly_signals.get('device_anomaly', {})
            if device_anom:
                summary_parts.append(f"- Dispositivo: {device_anom.get('reason', 'N/A')} (score: {device_anom.get('score', 0):.2f})")
            
            country_anom = anomaly_signals.get('country_anomaly', {})
            if country_anom:
                summary_parts.append(f"- País: {country_anom.get('reason', 'N/A')} (score: {country_anom.get('score', 0):.2f})")
        
        # Behavioral analysis
        if behavioral_analysis:
            deviation = behavioral_analysis.get('deviation_score', 0)
            summary_parts.append(f"\nDesviación de comportamiento: {deviation:.2f}")
            pattern = behavioral_analysis.get('pattern_deviation', '')
            if pattern:
                summary_parts.append(f"Análisis: {pattern}")
        
        return "\n".join(summary_parts)