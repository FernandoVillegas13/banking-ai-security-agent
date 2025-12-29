from domain.schema.schemas import AgentState
from langgraph.graph import StateGraph, START, END
from infraestructure.agents.transaction_context_agent import TransactionContextAgent
from infraestructure.agents.behavioral_agent import BehavioralAgent
from infraestructure.agents.internal_policy_rag_agent import InternalPolicyRAGAgent
from infraestructure.agents.external_threat_agent import ExternalThreatAgent
from infraestructure.agents.debate_agents import DebateAgent
from infraestructure.agents.decision_arbiter import DecisionArbiter
from infraestructure.agents.explainability_agent import ExplanabilityAgent
from infraestructure.agents.human_review_queue import HumanReviewQueue
from typing import Dict, Any


class LangGraphInit:

    def __init__(self, llm, redis_adapter=None):
        try:
            self.llm = llm
            self.runnable = self.build_graph()

            self.context_agent = TransactionContextAgent()
            self.behavioral_agent = BehavioralAgent(llm)
            self.policy_rag_agent = InternalPolicyRAGAgent()
            self.threat_agent = ExternalThreatAgent(llm)
            self.debate_agents = DebateAgent(llm)
            self.arbiter_agent = DecisionArbiter(llm)
            self.explainability_agent = ExplanabilityAgent(llm)
            self.human_review_queue = HumanReviewQueue(redis_adapter)

        except Exception as e:
            raise e

    def build_graph(self):

        def should_debate(state: AgentState) -> str:
            if state['anomaly_score'] > 0.75:  # Evidencia muy clara de APPROVE o BLOCK
                return "decision_arbiter"
            return "debate_agents"
        
        def final_routing(state: AgentState) -> str:
            print("Final routing based on decision and confidence")
            decision = state.get('decision', {})
            decision_value = decision.get('value')
            confidence = decision.get('confidence')
            print(f"Decision: {decision_value}, Confidence: {confidence}")
            
            if decision_value == "ESCALATE_TO_HUMAN" or confidence < 0.75:
                return "human_review_queue"
            return END  # Fin del proceso automático

        workflow = StateGraph(AgentState)
        workflow.add_node("transaction_context_agent", self._transaction_context_node)
        workflow.add_node("behavioral_agent", self._behavioral_agent)
        workflow.add_node("internal_policy_rag_agent", self._internal_policy_rag_agent)
        workflow.add_node("external_threat_agent", self._external_threat_agent)
        workflow.add_node("debate_agents", self._debate_agents)
        workflow.add_node("decision_arbiter", self._decision_arbiter)
        workflow.add_node("explainability_agent", self._explainability_agent)
        workflow.add_node("human_review_queue", self._human_review_queue)


        workflow.add_edge(START, "transaction_context_agent")
        workflow.add_edge("transaction_context_agent", "behavioral_agent")
        workflow.add_edge("behavioral_agent", "internal_policy_rag_agent")
        workflow.add_edge("internal_policy_rag_agent", "external_threat_agent")

        workflow.add_conditional_edges(
            "external_threat_agent",
            should_debate,
            {
                "debate_agents": "debate_agents",
                "decision_arbiter": "decision_arbiter"
            })

        workflow.add_edge("debate_agents", "decision_arbiter")
        workflow.add_edge("decision_arbiter", "explainability_agent")

        workflow.add_conditional_edges(
            "explainability_agent",
            final_routing,
            {
                "human_review_queue": "human_review_queue",
                END: END
            })

        graph = workflow.compile()
        return graph
    
    
    async def _transaction_context_node(self, state: AgentState) -> Dict[str, Any]:
        return await self.context_agent.analyze_transaction(state)
    
    async def _behavioral_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.behavioral_agent.analyze_behavior(state)
    
    async def _internal_policy_rag_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.policy_rag_agent.get_policies(state)
    
    async def _external_threat_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.threat_agent.get_external_threat(state)
    
    async def _debate_agents(self, state: AgentState) -> Dict[str, Any]:
        return await self.debate_agents.debate(state)
    
    async def _decision_arbiter(self, state: AgentState) -> Dict[str, Any]:
        return await self.arbiter_agent.decide(state)
    
    async def _explainability_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.explainability_agent.explain(state)
    
    async def _human_review_queue(self, state: AgentState) -> Dict[str, Any]:
        return await self.human_review_queue.escalate(state)


    def inspect_graph(self):
        graph = self.build_graph()
        print("Graph Nodes:")
        for node in graph.nodes:
            print(f"Node: {node.name}, Function: {node.func.__name__}")
        
        print("\nGraph Edges:")
        for edge in graph.edges:
            print(f"From: {edge[0].name} To: {edge[1].name}")
        
        return graph
    
    def invoke_graph(self,  **kwargs):
        result = self.runnable.invoke(input=AgentState(**kwargs))
        return result["messages"][-1].content