from typing import List, Literal

from pydantic import BaseModel, Field

Tier = Literal["S", "A", "B", "C", "D"]


class ListingEvaluation(BaseModel):
    """Evaluacion de un inmueble individual dentro del ranking por tiers."""

    rank: int = Field(description="Posicion en el ranking, 1 es la mejor opcion")
    tier: Tier = Field(description="S = ideal, A = muy buena, B = aceptable, C = con reservas, D = descartar")
    title: str
    url: str
    price: str
    location: str
    score: int = Field(ge=0, le=100, description="Puntaje global 0-100")
    summary: str = Field(description="Resumen de 1-2 frases de por que esta en ese tier")
    pros: List[str]
    cons: List[str]
    fits_budget: bool
    advisor_note: str = Field(description="Comentario tipo asesor: que negociar, que revisar en la visita, alertas")


class AgentAnalysis(BaseModel):
    """Respuesta completa del agente asesor."""

    headline: str = Field(description="Titular corto con la recomendacion principal")
    market_overview: str = Field(description="Lectura del mercado para esa zona y presupuesto, 1 parrafo")
    evaluations: List[ListingEvaluation]
    top_recommendation: str = Field(description="Explicacion detallada de la mejor opcion y por que")
    advice: List[str] = Field(description="Consejos practicos para el usuario (negociacion, documentos, visitas)")
    missing_info: List[str] = Field(default_factory=list, description="Datos que el usuario deberia aclarar para afinar la busqueda")
