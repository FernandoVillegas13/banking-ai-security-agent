from domain.schema.schemas import AgentState
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import json

class ExplanabilityAgent:
    def __init__(self, llm):
        self.llm = llm

    async def explain(self, state: AgentState) -> Dict[str, Any]:
        start_time = datetime.now()
        agent_audit = state.get('agent_audit', [])
        
        # Preparar contexto completo para el LLM
        context = self._prepare_context(state)
        
        # Generar explicación para el cliente
        explanation_customer = await self._generate_customer_explanation(context, state)
        
        # Generar explicación para auditoría
        explanation_audit = await self._generate_audit_explanation(context, state)
        
        # Register audit trail
        agent_audit.append({
            "agent_name": "explainability_agent",
            "explanations_generated": 2,
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": (datetime.now() - start_time).total_seconds()
        })
        
        return {
            "explanations": explanation_customer,
            "explanation_audit": explanation_audit,
            "agent_audit": agent_audit
        }
    
    def _prepare_context(self, state: AgentState) -> str:
                
        # Obtener datos del estado
        transaction_obj = state.get('transaction_request')
        # Convertir TransactionRequest a diccionario si es necesario
        if transaction_obj and hasattr(transaction_obj, 'dict'):
            transaction = transaction_obj.dict()
        else:
            transaction = transaction_obj or {}
        
        decision = state.get('decision', {})
        signals = state.get('signals', [])
        anomaly_score = state.get('anomaly_score', 0)
        anomaly_signals = state.get('anomaly_signals', {})
        behavioral_analysis = state.get('behavioral_analysis', {})
        rag_evidence = state.get('rag_evidence', [])
        search_evidence = state.get('search_evidence', [])
        
        context = f"""
        TRANSACCIÓN:
        - ID: {transaction.get('transaction_id')}
        - Cliente: {transaction.get('customer_id')}
        - Monto: {transaction.get('amount')} {transaction.get('currency')}
        - País: {transaction.get('country')}
        - Canal: {transaction.get('channel')}
        - Dispositivo: {transaction.get('device_id')}
        - Timestamp: {transaction.get('timestamp')}

        DECISIÓN TOMADA: {decision.get('value')}
        CONFIANZA: {decision.get('confidence', 0):.2f}

        SEÑALES DETECTADAS: {', '.join(signals) if signals else 'Ninguna'}

        ANÁLISIS DE ANOMALÍAS:
        {json.dumps(anomaly_signals, indent=2)}

        ANÁLISIS COMPORTAMENTAL:
        {json.dumps(behavioral_analysis, indent=2)}

        POLÍTICAS INTERNAS CONSULTADAS (RAG):
        {json.dumps(rag_evidence, indent=2)}

        INTELIGENCIA EXTERNA (WEB SEARCH):
        {json.dumps(search_evidence, indent=2)}

        RAZONAMIENTO DEL ÁRBITRO:
        {decision.get('chain_of_thought', '')}
        """
        return context
    
    async def _generate_customer_explanation(self, context: str, state: AgentState) -> str:        
        decision_value = state.get('decision', {}).get('value', 'UNKNOWN')
        
        system_prompt = SystemMessage(content="""
        Eres un asistente bancario que explica decisiones sobre transacciones a clientes.
        Tu objetivo es generar una explicación CLARA, BREVE y AMIGABLE que el cliente pueda entender fácilmente.

        Reglas:
        - Usa lenguaje simple y directo, sin términos técnicos
        - Sé cordial y profesional
        - Explica POR QUÉ se tomó la decisión
        - Si hay acciones que el cliente debe tomar, indícalas claramente
        - Máximo 2-3 párrafos
        - No menciones términos como "RAG", "agentes", "scores", etc.
        """)
                
        human_prompt = HumanMessage(content=f"""
        Basándote en la siguiente información, genera una explicación clara para el cliente sobre por qué su transacción fue marcada como {decision_value}.

        {context}

        Genera una explicación amigable y profesional para el cliente:
        """)
        
        response = await self.llm.ainvoke([system_prompt, human_prompt])
        return response.content.strip()
    
    async def _generate_audit_explanation(self, context: str, state: AgentState) -> str:
        """Genera una explicación técnica detallada para auditoría"""
        
        decision_value = state.get('decision', {}).get('value', 'UNKNOWN')
        
        system_prompt = SystemMessage(content="""
        Eres un sistema de auditoría bancaria que documenta decisiones de análisis de fraude.
        Tu objetivo es generar una explicación TÉCNICA pero CORTA para fines de auditoría y cumplimiento.

        Reglas:
        - Usa lenguaje técnico y preciso
        - CITA todas las fuentes: políticas internas, evidencia externa, scores
        - Documenta la RUTA COMPLETA del análisis (qué agentes participaron)
        - Menciona los factores considerados
        - Lista las políticas aplicadas con sus IDs y versiones
        - Justifica la decisión con evidencia concreta
        """)
        
        human_prompt = HumanMessage(content=f"""
        Basándote en la siguiente información completa del análisis, genera una explicación detallada para auditoría sobre la decisión {decision_value}.

        {context}

        IMPORTANTE: Incluye en tu explicación:
        1. Ruta de agentes ejecutados: Transaction Context → Behavioral → Policy RAG → External Threat → Debate → Decision Arbiter → Explainability
        2. Todas las políticas consultadas con sus IDs (policy_id) y versiones
        3. Señales detectadas y su impacto
        4. Razonamiento completo del árbitro

        Genera una explicación técnica para auditoría:
        """)
        
        response = await self.llm.ainvoke([system_prompt, human_prompt])
        return response.content.strip()