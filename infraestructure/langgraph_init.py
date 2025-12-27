from domain.schema.schemas import AgentState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage
from typing import Dict, Any


class LangGraphInit:

    def __init__(self, llm, tools):
        try:
            self.llm = llm
            self.tools = tools
            self.runnable = self.build_graph()
        except Exception as e:
            raise e

    def build_graph(self):

        def should_debate(state: AgentState) -> str:
            if state['confidence'] > 0.9:  # Evidencia muy clara de APPROVE o BLOCK
                return "decision_arbiter"
            return "debate_agents"
        
        def final_routing(state: AgentState) -> str:
            if state['decision'] == "ESCALATE_TO_HUMAN" or state['need_human_review']:
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
        return await self.context_agent.analyze(state)
    
    async def _behavioral_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.behavioral_agent.analyze(state)
    
    async def _internal_policy_rag_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.policy_agent.analyze(state)
    
    async def _external_threat_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.threat_agent.analyze(state)
    
    async def _debate_agents(self, state: AgentState) -> Dict[str, Any]:
        return await self.debate_agent.debate(state)
    
    async def _decision_arbiter(self, state: AgentState) -> Dict[str, Any]:
        return await self.arbiter_agent.decide(state)
    
    async def _explainability_agent(self, state: AgentState) -> Dict[str, Any]:
        return await self.explainability_agent.explain(state)
    
    async def _human_review_queue(self, state: AgentState) -> Dict[str, Any]:
        return await self.human_review_agent.escalate(state)


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