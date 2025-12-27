from unittest import result
from langchain_core.tools import tool
import pandas as pd
from sqlalchemy import text
from domain.schema.schemas import StateMessages, VegaLiteSpec
import json
import httpx
from jsonschema import validate, ValidationError

class Tools:

    def __init__(self, engine):
        self.engine = engine

    def obtener_tools(self):

        @tool
        def tool1(query: str):
            try:
                return json.dumps({
                    "status": "ok",
                })

            except Exception as e:
                return json.dumps({
                    "status": "error",
                })
            

        @tool
        async def tool2(vega_spec: VegaLiteSpec):
            try:    

                return json.dumps({
                    "status": "ok",
                }, indent=2)

            except Exception as e:
                return json.dumps({
                    "status": "error",
                })

        return [tool1, tool2]
    

