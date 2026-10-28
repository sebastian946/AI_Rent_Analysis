# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python 3.12 CLI that helps users find rental or sale properties in Colombia. Flow: the user describes what they have and want (budget, operation, property type, city, locality, vehicles) → a Playwright scraper queries real-estate portals (currently only Fincaraíz) → a Claude agent (official `anthropic` SDK, structured output) ranks every listing into tiers S/A/B/C/D and writes an advisor-style recommendation. Code comments, prompts and user-facing strings are in Spanish.

## Commands

Dependencies are managed with `uv` (lockfile `uv.lock`).

```
uv sync                                   # install deps into .venv
uv run playwright install chromium        # one-time browser install for the scraper
uv run python main.py                     # interactive run (headless scraping)
uv run python main.py --show-browser      # watch the scraper in a visible browser
uv run python main.py --json report.json  # also dump the full analysis as JSON
uv run python utils/web_scaraping.py      # scraper-only smoke test (visible browser, Enter to close)
uv run python -c "from config.config import settings"   # verify .env loads
```

There is no test suite or linter configured yet. Running `main.py` makes a real paid API call.

## Configuration

`config/config.py` exposes a `settings` singleton (pydantic-settings) loaded from the repo-root `.env` (path resolved relative to the file, so it works from any CWD). Required keys: `ANTHROPIC_API_KEY`, `DB_NAME`, `DB_PASSWORD` (see `.env.example`). Importing `config.config` instantiates `Settings()` at module load, so a missing `.env` raises `ValidationError` on import. The agent reads the API key from `settings`, not from the environment directly.

## Architecture

- `model/tools_model.py` — `WebSearchTool` is the user profile (price in COP, square_meters, vehicles, department, ubication, optional locality/query, property_type ∈ casa/apartamento/apartaestudio, service_type ∈ arriendo/venta); `search_location` joins locality + city for the portal search box. `Listing` is one scraped property (`GetWebSearchTool` is a backward-compatible alias).
- `model/agents_model.py` — the agent's structured output: `AgentAnalysis` (headline, market_overview, `evaluations`, top_recommendation, advice, missing_info) and `ListingEvaluation` (rank, tier, score 0-100, pros/cons, fits_budget, advisor_note). Changing these models changes the JSON schema sent to the model and the report printed by `main.py`.
- `utils/web_scaraping.py` (sic) — `WebScraping` class; build it with `WebScraping.from_search(search, headless=...)`. `scraping_page()` iterates `LIST_URL_RENT_PAGES` and returns `list[Listing]`. `scraping_fincaraiz()` drives the Ant Design UI (property-type select → operation radio group → location input → search). In each result card the first `<a>` is the agency logo; the listing is `a.lc-data`, with `.main-price`, `.lc-location`, `.lc-description` and `.lc-typologyContainer strong` (rooms/baths/m²). Selectors are Ant Design / `lc-*` class names and will break if the site changes. Adding a portal means a new entry in `LIST_URL_RENT_PAGES`, a `scraping_<portal>` method and a branch in `scraping_page()`.
- `agents/agent.py` — `RentAdvisorAgent.analyze(search, listings)` calls `client.beta.messages.parse` on `claude-opus-5-5` with `output_format=AgentAnalysis`, effort `high`, and server-side refusal fallbacks (`fallbacks="default"`). It sends at most `MAX_LISTINGS` (30) listings as JSON and raises on `refusal` / `max_tokens`. The system prompt holds the tier rubric and evaluation criteria.
- `main.py` — `collect_user_input()` (interactive prompts validated through `WebSearchTool`), `run()` (scrape → analyze → `print_report`), CLI flags `--show-browser` and `--json`.
