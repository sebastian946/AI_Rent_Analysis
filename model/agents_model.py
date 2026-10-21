from tools_model import GetWebSearchTool
from pydantic import BaseModel
from typing import List

class AgentAnalysis(BaseModel):
    list_items: List[GetWebSearchTool]
    query: str

class GetAnalysis(BaseModel):
    analysis: str
     