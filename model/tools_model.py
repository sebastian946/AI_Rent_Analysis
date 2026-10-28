from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

PropertyType = Literal["casa", "apartamento", "apartaestudio"]
ServiceType = Literal["arriendo", "venta"]


class WebSearchTool(BaseModel):
    """Lo que el usuario tiene y busca. Es la entrada del scraper y el contexto del agente."""

    price: int = Field(description="Presupuesto maximo en COP")
    square_meters: int = Field(description="Metros cuadrados minimos deseados")
    vehicles: int = Field(ge=0, description="Cantidad de vehiculos que necesitan parqueadero")
    department: str = Field(description="Departamento, ej. Antioquia")
    ubication: str = Field(description="Ciudad o municipio, ej. Medellin")
    locality: Optional[str] = Field(default=None, description="Barrio o localidad dentro de la ciudad")
    property_type: PropertyType
    service_type: ServiceType
    query: Optional[str] = Field(default=None, description="Notas libres del usuario (mascotas, cerca al metro, etc.)")

    @field_validator("department", "ubication", "locality", "query", mode="before")
    @classmethod
    def _strip(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @property
    def search_location(self) -> str:
        return f"{self.locality}, {self.ubication}" if self.locality else self.ubication


class Listing(BaseModel):
    """Un inmueble tal como lo devuelve el scraper."""

    url: str
    title: Optional[str] = None
    price: str
    distribution: List[str] = Field(default_factory=list, description="[habitaciones, banos, m2] como texto")
    location: str
    description: str
    web_app: str = "fincaraiz"


# Alias retrocompatible con el nombre original
GetWebSearchTool = Listing
