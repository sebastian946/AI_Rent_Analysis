"""Agente asesor inmobiliario: analiza los inmuebles raspados y los clasifica por tiers."""

import json
from typing import List

import anthropic

from config.config import settings
from model.agents_model import AgentAnalysis
from model.tools_model import Listing, WebSearchTool

MODEL = "claude-opus-5-5"
MAX_LISTINGS = 30

SYSTEM_PROMPT = """Eres un asesor inmobiliario senior en Colombia con experiencia en arriendo y venta de vivienda.
Tu trabajo es analizar una lista de inmuebles obtenida de portales web y entregar una recomendacion honesta,
detallada y util, como lo haria un asesor de confianza en una reunion con su cliente.

Criterios de evaluacion, en orden de importancia:
1. Ajuste al presupuesto (si lo supera notablemente, baja de tier; si lo supera poco, dilo y sugiere negociar).
2. Ajuste a la ubicacion y localidad pedida.
3. Tipo de inmueble, area (m2), habitaciones y banos frente a lo que el usuario necesita.
4. Parqueaderos frente a la cantidad de vehiculos.
5. Relacion precio/m2 comparada con el resto de la lista.
6. Senales de alerta en la descripcion (datos incompletos, precios sospechosamente bajos, etc.).

Escala de tiers:
- S: cumple todo y destaca; recomendacion principal.
- A: cumple lo esencial con un detalle menor.
- B: aceptable, con una o dos concesiones claras.
- C: con reservas importantes.
- D: descartar.

Reglas:
- Evalua TODOS los inmuebles recibidos y asigna un rank unico y consecutivo desde 1.
- Se concreto: cita precios, m2 y datos reales de cada anuncio. No inventes informacion que no este en los datos.
- Si un dato no aparece en el anuncio, dilo como una incognita y sugiere confirmarlo en la visita.
- Responde siempre en espanol, con tono cercano y profesional."""


def _listings_payload(listings: List[Listing]) -> str:
    rows = [
        {
            "id": i + 1,
            "title": item.title,
            "url": item.url,
            "price": item.price,
            "distribution": item.distribution,
            "location": item.location,
            "description": item.description,
            "source": item.web_app,
        }
        for i, item in enumerate(listings[:MAX_LISTINGS])
    ]
    return json.dumps(rows, ensure_ascii=False, indent=2)


def _user_profile(search: WebSearchTool) -> str:
    budget = f"{search.price:,.0f}".replace(",", ".")
    return "\n".join(
        [
            f"- Operacion: {search.service_type}",
            f"- Tipo de inmueble: {search.property_type}",
            f"- Presupuesto maximo: ${budget} COP",
            f"- Area minima deseada: {search.square_meters} m2",
            f"- Vehiculos (parqueaderos necesarios): {search.vehicles}",
            f"- Departamento: {search.department}",
            f"- Ciudad: {search.ubication}",
            f"- Localidad/barrio: {search.locality or 'sin preferencia'}",
            f"- Notas del usuario: {search.query or 'ninguna'}",
        ]
    )


class RentAdvisorAgent:
    def __init__(self, client: anthropic.Anthropic | None = None, model: str = MODEL):
        self.client = client or anthropic.Anthropic(
            api_key=settings.anthropic_api_key.get_secret_value()
        )
        self.model = model

    def analyze(self, search: WebSearchTool, listings: List[Listing]) -> AgentAnalysis:
        if not listings:
            raise ValueError("No hay inmuebles para analizar.")

        user_message = (
            "## Perfil del cliente\n"
            f"{_user_profile(search)}\n\n"
            "## Inmuebles encontrados (JSON)\n"
            f"{_listings_payload(listings)}\n\n"
            "Analiza cada inmueble, clasificalo por tier y entrega tu recomendacion como asesor."
        )

        response = self.client.beta.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            output_format=AgentAnalysis,
            output_config={"effort": "high"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        if response.stop_reason == "refusal":
            detail = response.stop_details.explanation if response.stop_details else ""
            raise RuntimeError(f"El modelo rechazo la solicitud. {detail}".strip())
        if response.stop_reason == "max_tokens":
            raise RuntimeError("La respuesta se corto por max_tokens; reduce la cantidad de inmuebles.")

        analysis = response.parsed_output
        analysis.evaluations.sort(key=lambda e: e.rank)
        return analysis
