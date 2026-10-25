from pydantic import BaseModel
from typing import Literal, List, Optional

class WebSearchTool(BaseModel):
    price: str
    square_meters: str
    vehicles: int
    department: str
    ubication: str
    property_type: Literal["casa","apartamento","apartaestudio"]
    service_type: Literal["arriendo","compra"]
    query: Optional[str] = None

class GetWebSearchTool(BaseModel):
    link: str
    price: str
    ubication: str
    description: str
    images: List[str]
    web_app: str


