-include .env
export

SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PIP := $(VENV)/bin/pip

PORT ?= 5508

.DEFAULT_GOAL := help

# ===================== INTERNAL HELPER =====================

$(VENV):
	@echo "ERROR: Virtual environment not found. Run 'make setup' first" && exit 1

# ===================== MANDATORY TARGETS =====================

help:
	@echo "Mandatory targets:"
	@echo "  make setup             Create venv and install dependencies (incl. PyTorch CPU)"
	@echo "  make test              Run pytest tests"
	@echo "  make docker-build      Build Docker image"
	@echo "  make docker-up         Start the service"
	@echo "  make docker-down       Stop the service"
	@echo "  make health            Check service health"
	@echo "  make predict           Post-game prediction (Neural Net, requires API key)"
	@echo "  make predict-pregame   Pre-game prediction: G2 vs MAD Lions (requires API key)"
	@echo ""
	@echo "Optional targets:"
	@echo "  make dev               Run API locally (uvicorn with hot-reload)"
	@echo "  make pipeline          Run data pipeline"
	@echo "  make train             Train models"
	@echo "  make logs              Tail Docker service logs"
	@echo "  make clean             Clean generated files"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	# PyTorch CPU-only (not in requirements.txt — avoids pulling the heavy CUDA build)
	$(PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install -r requirements.txt
	@echo "Setup complete. Activate with: source $(VENV)/bin/activate"

test: $(VENV)
	@test -d tests || (echo "ERROR: tests/ directory not found. Tests are added in Session 11." && exit 1)
	$(PYTEST) tests/ -v

docker-build:
	docker compose build

docker-up:
	mkdir -p data logs
	docker compose up -d
	@echo "Service started at http://localhost:$(PORT)"

docker-down:
	docker compose down

health:
	@set -o pipefail; curl -sf http://localhost:$(PORT)/health | python3 -m json.tool || \
	 (echo "ERROR: Service not responding at /health" && exit 1)

# ---------------------------------------------------------------------------
# Requires X-API-Key header. Set API_KEY in your .env or override:
#   make predict API_KEY=your-key-here
# ---------------------------------------------------------------------------
predict:
	@set -o pipefail; curl -sf -X POST http://localhost:$(PORT)/predict \
	 -H "Content-Type: application/json" \
	 -H "X-API-Key: $(API_KEY)" \
	 -d '{"team_encoded":"G2 Esports","player_encoded":"Caps","champion_encoded":"Azir","side_encoded":"Blue","position_encoded":"mid","team_winrate":0.65,"player_winrate":0.62,"player_kda":3.8,"champion_winrate":0.54,"player_champ_winrate":0.70,"kills":5,"deaths":2,"assists":8,"teamkills":24,"teamdeaths":10,"dragons":3,"opp_dragons":1,"elders":1,"opp_elders":0,"barons":2,"opp_barons":0,"towers":9,"opp_towers":3,"totalgold":14800}' \
	 | python3 -m json.tool || \
	 (echo "ERROR: Prediction failed. Is the service running? Does API_KEY have credits?" && exit 1)

predict-pregame:
	@set -o pipefail; curl -sf -X POST http://localhost:$(PORT)/predict/pregame \
	 -H "Content-Type: application/json" \
	 -H "X-API-Key: $(API_KEY)" \
	 -d '{ \
	   "team1": { \
	     "team_name": "G2 Esports", \
	     "side": "Blue", \
	     "players": [ \
	       {"player": "BrokenBlade", "champion": "K'\''Sante",  "position": "top"}, \
	       {"player": "Yike",        "champion": "Vi",        "position": "jng"}, \
	       {"player": "Caps",        "champion": "Azir",      "position": "mid"}, \
	       {"player": "Hans Sama",   "champion": "Varus",     "position": "bot"}, \
	       {"player": "Mikyx",       "champion": "Zyra",      "position": "sup"} \
	     ] \
	   }, \
	   "team2": { \
	     "team_name": "MAD Lions KOI", \
	     "side": "Red", \
	     "players": [ \
	       {"player": "Myrwn",     "champion": "Gwen",         "position": "top"}, \
	       {"player": "Elyoya",    "champion": "Viego",        "position": "jng"}, \
	       {"player": "Fresskowy", "champion": "Neeko",        "position": "mid"}, \
	       {"player": "Supa",      "champion": "Ashe",         "position": "bot"}, \
	       {"player": "Alvaro",    "champion": "Renata Glasc", "position": "sup"} \
	     ] \
	   } \
	 }' \
	 | python3 -m json.tool || \
	 (echo "ERROR: Pre-game prediction failed. Is the service running? Does API_KEY have credits?" && exit 1)

# ===================== OPTIONAL TARGETS =====================

dev: $(VENV)
	$(VENV)/bin/uvicorn app.api:app --reload --port 8000

pipeline: $(VENV)
	$(PYTHON) -m app.ml.pipeline

train: $(VENV)
	$(PYTHON) -m app.ml.train

logs:
	docker compose logs -f api

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.parquet data/predictions.jsonl
	rm -f logs/*.log
	@echo "Cleaned"