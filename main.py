import json
from pydantic import BaseModel

def print_pretty(obj):
    import json
    from pydantic import BaseModel

    def default(o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        return str(o)

    print(json.dumps(obj, indent=2, ensure_ascii=False, default=default))

from fastapi import FastAPI
from pydantic import BaseModel
import os
# from infraestructure.langgraph_init import LangGraphInit
# from infraestructure.openai_client import OpenAIClient
# from domain.tools import Tools
from typing import Annotated, List, Generator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessageChunk
from langgraph.graph.message import add_messages
from contextlib import asynccontextmanager
from infraestructure.database_deepfeel import DataBaseDeepFeel
from infraestructure.redis_adapter import RedisAdapter
from domain.prompt_selector import PromptSelector
from infraestructure.materialized_views.selector_tabla import SelectorTabla
from domain.parseador_result import ParseadorResult
from domain.schema.schemas import TransactionRequest, UsualBehavior, AgentState
from application.search_usual import SearchUsual


redis = RedisAdapter()
search_usual = SearchUsual()
app = FastAPI()


@app.post("/analize")
async def chat(request: TransactionRequest):
    try:
        print("-----"*25)
        print("Received request:", request)

        ##Conseguir comportamiento usual del cliente
        usual_behavior = search_usual.get_usual_behavior_by_customer_id(request.customer_id)
        print("Usual behavior found:")
        print_pretty(usual_behavior)

        state = AgentState(
            transaction_request=request,
            usual_behavior=usual_behavior
        )

        print("Initial Agent State:")
        print_pretty(state)
        
        # result = await graph.ainvoke(input=state, config=config)

        # messages = result["messages"] if isinstance(result, dict) else result.messages
        # last_message = messages[-1]
        # content = last_message.content if hasattr(last_message, "content") else last_message.get("content")

        print("-----"*25)

        return {"response": "ok"}

    
    except Exception as e:
        print("Error processing:", str(e))
        return {
            "status": "error", 
            "message": str(e)
            }