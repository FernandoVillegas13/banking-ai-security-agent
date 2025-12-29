from langchain_openai import ChatOpenAI
import os

class OpenAIClient:
    
    def __init__(self):
        
        model = os.getenv("OPEN_AI_MODEL")
        model = "gpt-4.1-mini-2025-04-14"

        temperature = 0.2

        self.llm = ChatOpenAI(
                    name="Agent",
                    model_name=model,
                    temperature=temperature)        
    def get_llm(self):
        return self.llm