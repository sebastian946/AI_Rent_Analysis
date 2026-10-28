"""AI Rent Analysis: perfil del usuario -> scraping -> analisis del agente por tiers."""

import argparse
import json
import sys
from typing import Optional

from pydantic import ValidationError

from model.agents_model import AgentAnalysis
from model.tools_model import WebSearchTool
from services.analysis import NoListingsFound, run_analysis

TIER_LABEL = {
    "S": "S  Ideal",
    "A": "A  Muy buena",
    "B": "B  Aceptable",
    "C": "C  Con reservas",
    "D": "D  Descartar",
}


def _ask(prompt: str, default: Optional[str] = None, choices: Optional[list[str]] = None) -> str:
    hint = f" [{'/'.join(choices)}]" if choices else ""
    hint += f" (default: {default})" if default else ""
    while True:
        value = input(f"{prompt}{hint}: ").strip()
        if not value and default is not None:
            value = default
        if choices and value.lower() not in choices:
            print(f"  Opcion invalida. Elige una de: {', '.join(choices)}")
            continue
        if value or default is not None:
            return value.lower() if choices else value
        print("  Este dato es obligatorio.")


def collect_user_input() -> WebSearchTool:
    print("=== AI Rent Analysis ===\nCuentame que tienes y que buscas.\n")
    while True:
        try:
            return WebSearchTool(
                service_type=_ask("Buscas arriendo o venta", choices=["arriendo", "venta"]),
                property_type=_ask("Tipo de inmueble", choices=["casa", "apartamento", "apartaestudio"]),
                price=_ask("Presupuesto maximo en COP (ej. 2500000)"),
                square_meters=_ask("Metros cuadrados minimos", default="40"),
                vehicles=_ask("Cuantos vehiculos tienes", default="0"),
                department=_ask("Departamento (ej. Antioquia)"),
                ubication=_ask("Ciudad o municipio (ej. Medellin)"),
                locality=_ask("Localidad o barrio (opcional)", default=""),
                query=_ask("Algo mas que debamos saber (mascotas, cerca al metro...)", default=""),
            )
        except ValidationError as exc:
            print("\nHay datos invalidos:")
            for err in exc.errors():
                print(f"  - {'.'.join(str(p) for p in err['loc'])}: {err['msg']}")
            print("Intentemos de nuevo.\n")


def print_report(analysis: AgentAnalysis) -> None:
    line = "=" * 72
    print(f"\n{line}\n{analysis.headline}\n{line}\n")
    print("PANORAMA DEL MERCADO\n" + analysis.market_overview + "\n")

    print("RANKING POR TIERS")
    for ev in analysis.evaluations:
        budget = "dentro del presupuesto" if ev.fits_budget else "FUERA del presupuesto"
        print(f"\n#{ev.rank}  [{TIER_LABEL[ev.tier]}]  {ev.score}/100  {ev.title}")
        print(f"    {ev.price}  |  {ev.location}  |  {budget}")
        print(f"    {ev.url}")
        print(f"    {ev.summary}")
        for p in ev.pros:
            print(f"      + {p}")
        for c in ev.cons:
            print(f"      - {c}")
        print(f"    Asesor: {ev.advisor_note}")

    print(f"\n{line}\nRECOMENDACION PRINCIPAL\n{analysis.top_recommendation}\n")
    print("CONSEJOS")
    for tip in analysis.advice:
        print(f"  * {tip}")
    if analysis.missing_info:
        print("\nPARA AFINAR LA BUSQUEDA")
        for item in analysis.missing_info:
            print(f"  ? {item}")
    print()


def run(search: WebSearchTool, headless: bool, output_json: Optional[str]) -> int:
    try:
        _, analysis = run_analysis(search, headless=headless, on_progress=lambda m: print(m))
    except NoListingsFound as exc:
        print(f"{exc} Prueba otra ubicacion o tipo de inmueble.")
        return 1
    print_report(analysis)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as fh:
            json.dump(analysis.model_dump(), fh, ensure_ascii=False, indent=2)
        print(f"Reporte guardado en {output_json}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Analisis de arriendo/venta con IA")
    parser.add_argument("--show-browser", action="store_true", help="Muestra el navegador durante el scraping")
    parser.add_argument("--json", metavar="FILE", help="Guarda el analisis completo en un archivo JSON")
    args = parser.parse_args()

    try:
        search = collect_user_input()
        return run(search, headless=not args.show_browser, output_json=args.json)
    except KeyboardInterrupt:
        print("\nCancelado.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
