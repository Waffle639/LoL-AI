

-include .env
export

SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PIP := $(VENV)/bin/pip
RUN_DIR := .run
PID_FILE := $(RUN_DIR)/services.pid
PYTEST_OPTS ?= -vv --color=yes --tb=short -r fEsxX --disable-warnings

# PORT is read from .env (via -include above). This line is a safety fallback
# only when PORT is not defined in .env at all.
PORT ?= 8000

.DEFAULT_GOAL := help

# ===================== INTERNAL HELPER =====================

$(VENV):
	@echo "ERROR: Virtual environment not found. Run 'make setup' first" && exit 1

# ===================== MANDATORY TARGETS =====================

help:
	@echo "Mandatory targets:"
	@echo "  make setup             Create venv and install dependencies (incl. PyTorch CPU)"
	@echo "  make dvc               Configure DVC remote credentials and pull data/models"
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
	@echo "  make start-api         Start backend API in dev mode"
	@echo "  make start-landing     Start landing app (Vite)"
	@echo "  make start-dashboard   Start dashboard app (Vite)"
	@echo "  make start-all         Start API + landing + dashboard together"
	@echo "  make stop-all          Stop all services started by start-all"
	@echo "  make pipeline          Run data pipeline"
	@echo "  make train             Train models"
	@echo "  make logs              Tail Docker service logs"
	@echo "  make clean             Clean generated files"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	# PyTorch CPU-only (not in requirements.txt — avoids pulling the heavy CUDA build)
	$(PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install -r backend/requirements.txt
	@echo "Setup complete. Activate with: source $(VENV)/bin/activate"

# ===================== DVC =====================
# Configure DVC credentials for the DagsHub remote and pull all tracked files.
# Credentials are read from .env (DAGSHUB_USER / DAGSHUB_TOKEN).
# If the password is already stored in .dvc/config.local the configuration
# step is skipped and only the pull is executed.
#
# Usage:
#   make dvc                          # uses DAGSHUB_USER / DAGSHUB_TOKEN from .env
#   make dvc DAGSHUB_TOKEN=<token>    # one-off override
# ---------------------------------------------------------------------------
dvc: $(VENV)
	@test -n "$(DAGSHUB_USER)"  || (echo "ERROR: DAGSHUB_USER is not set in .env" && exit 1)
	@test -n "$(DAGSHUB_TOKEN)" || (echo "ERROR: DAGSHUB_TOKEN is not set in .env" && exit 1)
	@echo "Configuring DVC remote credentials..."
	@$(VENV)/bin/dvc remote modify dagshub --local auth basic
	@$(VENV)/bin/dvc remote modify dagshub --local user "$(DAGSHUB_USER)"
	@$(VENV)/bin/dvc remote modify dagshub --local password "$(DAGSHUB_TOKEN)"
	@echo "Credentials saved to .dvc/config.local"
	$(VENV)/bin/dvc pull

test: $(VENV)
	@test -d backend/tests || (echo "ERROR: backend/tests/ directory not found." && exit 1)
	$(PYTEST) backend/tests/ $(PYTEST_OPTS)

docker-build:
	docker compose build

docker-up:
	mkdir -p data logs
	chmod a+w logs
	docker compose up -d
	@echo "Service started at http://localhost:$(PORT)"

docker-down:
	docker compose down


docker-test:
	docker build --target test -t firemaw-test .
	docker run --rm firemaw-test pytest backend/tests $(PYTEST_OPTS)
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
	cd backend && ../$(VENV)/bin/uvicorn app.api:app --reload --host 0.0.0.0 --port $(PORT)

start-api: dev

start-landing:
	cd frontend/landing && npm run dev

start-dashboard:
	cd frontend/dashboard && npm run dev

start-all:
	@set -e; \
	ROOT_DIR="$(CURDIR)"; \
	PID_FILE_PATH="$$ROOT_DIR/$(PID_FILE)"; \
	LOG_DIR="$$ROOT_DIR/logs"; \
	mkdir -p "$$LOG_DIR" "$$ROOT_DIR/$(RUN_DIR)"; \
	if [ -f "$$PID_FILE_PATH" ] && [ -s "$$PID_FILE_PATH" ]; then \
		echo "ERROR: $$PID_FILE_PATH already exists. Run 'make stop-all' first."; \
		exit 1; \
	fi; \
	: > "$$PID_FILE_PATH"; \
	(cd "$$ROOT_DIR/backend" && nohup "$$ROOT_DIR/$(VENV)/bin/uvicorn" app.api:app --reload --host 0.0.0.0 --port $(PORT) > "$$LOG_DIR/api.dev.log" 2>&1 & echo $$! >> "$$PID_FILE_PATH"); \
	(cd "$$ROOT_DIR/frontend/landing" && nohup npm run dev -- --host 0.0.0.0 > "$$LOG_DIR/landing.dev.log" 2>&1 & echo $$! >> "$$PID_FILE_PATH"); \
	(cd "$$ROOT_DIR/frontend/dashboard" && nohup npm run dev -- --host 0.0.0.0 > "$$LOG_DIR/dashboard.dev.log" 2>&1 & echo $$! >> "$$PID_FILE_PATH"); \
	echo "Services started. PIDs:"; cat "$$PID_FILE_PATH"; \
	echo "API: http://localhost:$(PORT) | Landing: http://localhost:5173 | Dashboard: http://localhost:5174"

stop-all:
	@set -e; \
	ROOT_DIR="$(CURDIR)"; \
	PID_FILE_PATH="$$ROOT_DIR/$(PID_FILE)"; \
	if [ ! -f "$$PID_FILE_PATH" ] || [ ! -s "$$PID_FILE_PATH" ]; then \
		echo "No PID file found at $$PID_FILE_PATH. Nothing to stop."; \
		exit 0; \
	fi; \
	while read -r pid; do \
		if kill -0 $$pid 2>/dev/null; then \
			kill $$pid 2>/dev/null || true; \
			echo "Stopped PID $$pid"; \
		else \
			echo "PID $$pid not running"; \
		fi; \
	done < "$$PID_FILE_PATH"; \
	rm -f "$$PID_FILE_PATH"; \
	echo "All tracked services stopped."

pipeline: $(VENV)
	cd backend && ../$(PYTHON) -m app.ml.pipeline

train: $(VENV)
	cd backend && ../$(PYTHON) -m app.ml.train

logs:
	docker compose logs -f api

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.parquet data/predictions.jsonl
	rm -f logs/*.log
	@echo "Cleaned"