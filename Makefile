

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
LANDING_PORT ?= 5173
DASHBOARD_PORT ?= 5174

.DEFAULT_GOAL := help

# ===================== INTERNAL HELPER =====================

$(VENV):
	@echo "ERROR: Virtual environment not found. Run 'make setup' first" && exit 1

# ===================== MANDATORY TARGETS =====================

help:
	@echo "Available targets:"
	@echo "  make setup             Create venv and install dependencies (incl. PyTorch CPU)"
	@echo "  make dvc               Configure DVC credentials and pull tracked files"
	@echo "  make test              Run pytest tests"
	@echo "  make docker-build      Build Docker image"
	@echo "  make docker-up         Start service with Docker Compose"
	@echo "  make docker-down       Stop Docker Compose services"
	@echo "  make docker-test       Build test image and run backend tests in Docker"
	@echo "  make health            Check /health endpoint"
	@echo "  make predict           Post-game prediction request"
	@echo "  make predict-pregame   Pre-game prediction request"
	@echo "  make start-api         Run API locally with hot reload"
	@echo "  make start-landing     Start landing app (Vite)"
	@echo "  make start-dashboard   Start dashboard app (Vite)"
	@echo "  make start-all         Start API + landing + dashboard"
	@echo "  make stop-all          Stop processes started by start-all"
	@echo "  make pipeline          Run ML data pipeline"
	@echo "  make train             Train ML models"
	@echo "  make logs              Tail Docker API logs"
	@echo "  make clean             Remove generated/cached files"
	@echo ""
	@echo "Common options (override as needed):"
	@echo "  PORT=8000              API port (default from .env, fallback 8000)"
	@echo "  LANDING_PORT=5173      Landing port (default from .env, fallback 5173)"
	@echo "  DASHBOARD_PORT=5174    Dashboard port (default from .env, fallback 5174)"
	@echo "  API_KEY=<key>          Required for predict and predict-pregame"
	@echo "  PYTEST_OPTS='...'      Extra pytest flags (used by test and docker-test)"
	@echo "  DAGSHUB_USER=<user>    DVC remote username (for make dvc)"
	@echo "  DAGSHUB_TOKEN=<token>  DVC remote token (for make dvc)"

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
	@test -n "$(API_KEY)" || (echo "ERROR: API_KEY is empty. Set it in .env or run: make predict API_KEY=<key>" && exit 1)
	@tmp_file="$$(mktemp)"; \
	status="$$(curl -sS -o "$$tmp_file" -w "%{http_code}" -X POST http://localhost:$(PORT)/predict \
	 -H "Content-Type: application/json" \
	 -H "X-API-Key: $(API_KEY)" \
	 -d '{"team_encoded":"G2 Esports","player_encoded":"Caps","champion_encoded":"Azir","side_encoded":"Blue","position_encoded":"mid","team_winrate":0.65,"player_winrate":0.62,"player_kda":3.8,"champion_winrate":0.54,"player_champ_winrate":0.70,"kills":5,"deaths":2,"assists":8,"teamkills":24,"teamdeaths":10,"dragons":3,"opp_dragons":1,"elders":1,"opp_elders":0,"barons":2,"opp_barons":0,"towers":9,"opp_towers":3,"totalgold":14800}')" || { \
		echo "ERROR: Could not connect to API at http://localhost:$(PORT). Is the service running?"; \
		rm -f "$$tmp_file"; \
		exit 1; \
	}; \
	python3 -m json.tool < "$$tmp_file" 2>/dev/null || cat "$$tmp_file"; \
	if [ "$$status" -lt 200 ] || [ "$$status" -ge 300 ]; then \
		echo "ERROR: Prediction request failed with HTTP $$status."; \
		rm -f "$$tmp_file"; \
		exit 1; \
	fi; \
	rm -f "$$tmp_file"

predict-pregame:
	@test -n "$(API_KEY)" || (echo "ERROR: API_KEY is empty. Set it in .env or run: make predict-pregame API_KEY=<key>" && exit 1)
	@tmp_file="$$(mktemp)"; \
	status="$$(curl -sS -o "$$tmp_file" -w "%{http_code}" -X POST http://localhost:$(PORT)/predict/pregame \
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
	 }')" || { \
		echo "ERROR: Could not connect to API at http://localhost:$(PORT). Is the service running?"; \
		rm -f "$$tmp_file"; \
		exit 1; \
	}; \
	python3 -m json.tool < "$$tmp_file" 2>/dev/null || cat "$$tmp_file"; \
	if [ "$$status" -lt 200 ] || [ "$$status" -ge 300 ]; then \
		echo "ERROR: Pre-game prediction failed with HTTP $$status."; \
		rm -f "$$tmp_file"; \
		exit 1; \
	fi; \
	rm -f "$$tmp_file"

# ===================== OPTIONAL TARGETS =====================

start-api: $(VENV)
	@occupied_info="$$(ss -ltnp 2>/dev/null | awk '$$4 ~ /:$(PORT)$$/ {print $$0}' | head -n1)"; \
	if [ -n "$$occupied_info" ]; then \
		echo "Port $(PORT) is already in use:"; \
		echo "$$occupied_info"; \
		echo "Stop that process or run on another port: make start-api PORT=8001"; \
		exit 1; \
	fi; \
	cd backend && ../$(VENV)/bin/uvicorn app.api:app --reload --host 0.0.0.0 --port $(PORT)

start-landing:
	cd frontend/landing && npm run dev -- --host 0.0.0.0 --port $(LANDING_PORT) --strictPort

start-dashboard:
	cd frontend/dashboard && npm run dev -- --host 0.0.0.0 --port $(DASHBOARD_PORT) --strictPort

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
	(cd "$$ROOT_DIR/frontend/landing" && nohup npm run dev -- --host 0.0.0.0 --port $(LANDING_PORT) --strictPort > "$$LOG_DIR/landing.dev.log" 2>&1 & echo $$! >> "$$PID_FILE_PATH"); \
	(cd "$$ROOT_DIR/frontend/dashboard" && nohup npm run dev -- --host 0.0.0.0 --port $(DASHBOARD_PORT) --strictPort > "$$LOG_DIR/dashboard.dev.log" 2>&1 & echo $$! >> "$$PID_FILE_PATH"); \
	echo "Services started. PIDs:"; cat "$$PID_FILE_PATH"; \
	echo "API: http://localhost:$(PORT) | Landing: http://localhost:$(LANDING_PORT) | Dashboard: http://localhost:$(DASHBOARD_PORT)"

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