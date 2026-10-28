"""Servicio compartido por el CLI y el backend: scraping + analisis del agente."""

from typing import Callable, List, Optional

from agents.agent import RentAdvisorAgent
from model.agents_model import AgentAnalysis
from model.tools_model import Listing, WebSearchTool
from utils.web_scaraping import WebScraping

ProgressCallback = Callable[[str], None]


class NoListingsFound(Exception):
    """El scraper no encontro inmuebles para los criterios dados."""


def scrape_listings(search: WebSearchTool, headless: bool = True) -> List[Listing]:
    scraper = WebScraping.from_search(search, headless=headless)
    try:
        return scraper.scraping_page()
    finally:
        scraper.close()


def run_analysis(
    search: WebSearchTool,
    headless: bool = True,
    on_progress: Optional[ProgressCallback] = None,
) -> tuple[List[Listing], AgentAnalysis]:
    """Ejecuta el flujo completo y devuelve (inmuebles, analisis)."""
    notify = on_progress or (lambda _msg: None)

    notify(f"Buscando {search.property_type} en {search.service_type} en {search.search_location}...")
    listings = scrape_listings(search, headless=headless)
    if not listings:
        raise NoListingsFound("No se encontraron inmuebles con esos criterios.")

    notify(f"{len(listings)} inmuebles encontrados. Analizando con el asesor...")
    analysis = RentAdvisorAgent().analyze(search, listings)
    notify("Analisis completado.")
    return listings, analysis
