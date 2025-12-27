from langchain_openai import ChatOpenAI
import os

class OpenAIClient:
    
    def __init__(self, tools):
        model = os.getenv("OPEN_AI_MODEL")
        temperature = 0.2

        self.llm = ChatOpenAI(
                    name="Agent",
                    model_name=model,
                    temperature=temperature
                ).bind_tools(tools)
        
    def get_llm(self):
        return self.llm