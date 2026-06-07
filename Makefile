-include .env
export

SHELL := /bin/bash

VENV        := .venv
PYTHON      := $(VENV)/bin/python
PYTEST      := $(VENV)/bin/pytest
PIP         := $(VENV)/bin/pip
RUN_DIR     := .run
PID_FILE    := $(RUN_DIR)/services.pid
LOG_DIR     := logs
PYTEST_OPTS ?= -vv --color=yes --tb=short -r fEsxX --disable-warnings

PORT           ?= 8000
LANDING_PORT   ?= 5173
DASHBOARD_PORT ?= 5174

.DEFAULT_GOAL := help

# ─────────────────────────────────────────────
# INTERNAL: libera un puerto matando lo que haya
# Uso: $(call _free_port,8000)
# ─────────────────────────────────────────────
define _free_port
	@{ \
		pids=$$(lsof -ti :$(1) 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo "[port $(1)] ocupado por PID $$pids — matando..."; \
			kill $$pids 2>/dev/null || true; \
			sleep 0.5; \
			pids2=$$(lsof -ti :$(1) 2>/dev/null); \
			if [ -n "$$pids2" ]; then \
				echo "[port $(1)] SIGTERM ignorado, usando SIGKILL..."; \
				kill -9 $$pids2 2>/dev/null || true; \
				sleep 0.3; \
			fi; \
			echo "[port $(1)] libre."; \
		fi; \
	}
endef

# ─────────────────────────────────────────────
# INTERNAL: comprueba que el venv existe
# ─────────────────────────────────────────────
$(VENV):
	@echo "ERROR: Venv no encontrado. Ejecuta 'make setup' primero." && exit 1

# ══════════════════════════════════════════════
# AYUDA
# ══════════════════════════════════════════════
help:
	@echo ""
	@echo "  LoL-AI — comandos disponibles"
	@echo "  ─────────────────────────────────────────────────────"
	@echo "  SETUP"
	@echo "    make setup              Crear venv e instalar dependencias"
	@echo "    make dvc                Configurar credenciales DVC y hacer pull"
	@echo ""
	@echo "  DESARROLLO LOCAL"
	@echo "    make start              Arrancar API (mata el puerto si está ocupado)"
	@echo "    make restart            Matar y rearrancar la API"
	@echo "    make stop               Matar todo lo que esté en el puerto de la API"
	@echo "    make start-all          Arrancar API + landing + dashboard en background"
	@echo "    make restart-all        Parar y rearrancar todos los servicios"
	@echo "    make stop-all           Parar los servicios de start-all"
	@echo ""
	@echo "  TESTS Y CALIDAD"
	@echo "    make test               Ejecutar pytest"
	@echo "    make health             Comprobar /health"
	@echo ""
	@echo "  DOCKER"
	@echo "    make docker-build       Build de la imagen"
	@echo "    make docker-up          Levantar con Docker Compose"
	@echo "    make docker-down        Parar Docker Compose"
	@echo "    make docker-test        Tests en Docker"
	@echo "    make logs               Tail de logs del contenedor"
	@echo ""
	@echo "  ML"
	@echo "    make train              Entrenar modelos"
	@echo "    make pipeline           Ejecutar pipeline de datos ML"
	@echo ""
	@echo "  PRUEBAS DE API"
	@echo "    make predict            Petición de predicción in-game  (API_KEY requerida)"
	@echo "    make predict-pregame    Petición pre-game               (API_KEY requerida)"
	@echo ""
	@echo "  LIMPIEZA"
	@echo "    make clean              Borrar cachés y archivos generados"
	@echo ""
	@echo "  Variables override: PORT=8000  LANDING_PORT=5173  DASHBOARD_PORT=5174"
	@echo "                      API_KEY=<key>  PYTEST_OPTS='...'"
	@echo ""

# ══════════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════════
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install -r requirements.txt
	@echo "✓ Setup completo. Activa con: source $(VENV)/bin/activate"

# ══════════════════════════════════════════════
# DVC
# ══════════════════════════════════════════════
dvc: $(VENV)
	@test -n "$(DAGSHUB_USER)"  || (echo "ERROR: DAGSHUB_USER no definido en .env" && exit 1)
	@test -n "$(DAGSHUB_TOKEN)" || (echo "ERROR: DAGSHUB_TOKEN no definido en .env" && exit 1)
	@echo "Configurando credenciales DVC..."
	$(VENV)/bin/dvc remote modify dagshub --local auth basic
	$(VENV)/bin/dvc remote modify dagshub --local user     "$(DAGSHUB_USER)"
	$(VENV)/bin/dvc remote modify dagshub --local password "$(DAGSHUB_TOKEN)"
	@echo "Credenciales guardadas en .dvc/config.local"
	$(VENV)/bin/dvc pull

# ══════════════════════════════════════════════
# DESARROLLO LOCAL — API
# ══════════════════════════════════════════════

## Arranca la API; si el puerto está ocupado lo libera automáticamente
start: $(VENV)
	$(call _free_port,$(PORT))
	cd backend && ../$(VENV)/bin/uvicorn app.api:app --reload --host 0.0.0.0 --port $(PORT)

## Para lo que esté en el puerto de la API
stop:
	$(call _free_port,$(PORT))
	@echo "Puerto $(PORT) liberado."

## Mata y rearrancar la API (útil tras cambios de configuración)
restart: stop start

# ══════════════════════════════════════════════
# DESARROLLO LOCAL — TODOS LOS SERVICIOS
# ══════════════════════════════════════════════

## Arranca API + landing + dashboard en background
start-all: $(VENV)
	@mkdir -p $(LOG_DIR) $(RUN_DIR)
	@if [ -s $(PID_FILE) ]; then \
		echo "AVISO: $(PID_FILE) ya existe. Parando servicios anteriores..."; \
		$(MAKE) stop-all; \
	fi
	$(call _free_port,$(PORT))
	$(call _free_port,$(LANDING_PORT))
	$(call _free_port,$(DASHBOARD_PORT))
	@: > $(PID_FILE)
	@(cd backend && { nohup ../$(VENV)/bin/uvicorn app.api:app --reload \
	    --host 0.0.0.0 --port $(PORT) \
	    > ../$(LOG_DIR)/api.log 2>&1 & \
	    echo $$! >> ../$(PID_FILE); })
	@(cd frontend/landing && { nohup npm run dev -- \
	    --host 0.0.0.0 --port $(LANDING_PORT) --strictPort \
	    > ../../$(LOG_DIR)/landing.log 2>&1 & \
	    echo $$! >> ../../$(PID_FILE); })
	@(cd frontend/dashboard && { nohup npm run dev -- \
	    --host 0.0.0.0 --port $(DASHBOARD_PORT) --strictPort \
	    > ../../$(LOG_DIR)/dashboard.log 2>&1 & \
	    echo $$! >> ../../$(PID_FILE); })
	@sleep 1
	@echo ""
	@echo "  ✓ Servicios arrancados"
	@echo "    API       → http://localhost:$(PORT)"
	@echo "    Landing   → http://localhost:$(LANDING_PORT)"
	@echo "    Dashboard → http://localhost:$(DASHBOARD_PORT)"
	@echo "    Logs      → $(LOG_DIR)/"
	@echo ""

## Para los servicios lanzados por start-all
stop-all:
	@if [ ! -s $(PID_FILE) ]; then \
		echo "No hay servicios registrados en $(PID_FILE). Nada que parar."; \
		exit 0; \
	fi
	@while read -r pid; do \
		if kill -0 $$pid 2>/dev/null; then \
			kill $$pid 2>/dev/null && echo "  ✓ Parado PID $$pid" || true; \
		else \
			echo "  — PID $$pid ya no estaba activo"; \
		fi; \
	done < $(PID_FILE)
	@rm -f $(PID_FILE)
	@echo "Todos los servicios parados."

## Para y rearrancar todos los servicios
restart-all: stop-all start-all

# ══════════════════════════════════════════════
# TESTS Y CALIDAD
# ══════════════════════════════════════════════
test: $(VENV)
	@test -d backend/tests || (echo "ERROR: directorio backend/tests/ no encontrado." && exit 1)
	$(PYTEST) backend/tests/ $(PYTEST_OPTS)

health:
	@set -o pipefail; \
	curl -sf http://localhost:$(PORT)/health | python3 -m json.tool \
	|| (echo "ERROR: El servicio no responde en /health" && exit 1)

# ══════════════════════════════════════════════
# DOCKER
# ══════════════════════════════════════════════
docker-build:
	docker compose build

docker-up:
	mkdir -p data logs
	chmod a+w logs
	docker compose up -d
	@echo "Servicio en http://localhost:$(PORT)"

docker-down:
	docker compose down

docker-test:
	docker build --target test -t lolai-test .
	docker run --rm lolai-test pytest backend/tests $(PYTEST_OPTS)

logs:
	docker compose logs -f api

# ══════════════════════════════════════════════
# ML
# ══════════════════════════════════════════════
train: $(VENV)
	$(PYTHON) -m app.train

pipeline: $(VENV)
	$(PYTHON) -m app.ml.pipeline

# ══════════════════════════════════════════════
# PRUEBAS DE API (curl de ejemplo)
# ══════════════════════════════════════════════
predict:
	@test -n "$(API_KEY)" || (echo "ERROR: API_KEY vacía. Úsala así: make predict API_KEY=<clave>" && exit 1)
	@tmp=$$(mktemp); \
	status=$$(curl -sS -o "$$tmp" -w "%{http_code}" \
	  -X POST http://localhost:$(PORT)/predict \
	  -H "Content-Type: application/json" \
	  -H "X-API-Key: $(API_KEY)" \
	  -d '{"team_encoded":"G2 Esports","player_encoded":"Caps","champion_encoded":"Azir", \
	       "side_encoded":"Blue","position_encoded":"mid","team_winrate":0.65, \
	       "player_winrate":0.62,"player_kda":3.8,"champion_winrate":0.54, \
	       "player_champ_winrate":0.70,"kills":5,"deaths":2,"assists":8, \
	       "teamkills":24,"teamdeaths":10,"dragons":3,"opp_dragons":1, \
	       "elders":1,"opp_elders":0,"barons":2,"opp_barons":0, \
	       "towers":9,"opp_towers":3,"totalgold":14800}') 
	|| { echo "ERROR: No se puede conectar a http://localhost:$(PORT)"; rm -f "$$tmp"; exit 1; }; \
	python3 -m json.tool < "$$tmp" 2>/dev/null || cat "$$tmp"; \
	rm -f "$$tmp"; \
	[ "$$status" -ge 200 ] && [ "$$status" -lt 300 ] \
	|| (echo "ERROR: HTTP $$status" && exit 1)

predict-pregame:
	@test -n "$(API_KEY)" || (echo "ERROR: API_KEY vacía. Úsala así: make predict-pregame API_KEY=<clave>" && exit 1)
	@tmp=$$(mktemp); \
	status=$$(curl -sS -o "$$tmp" -w "%{http_code}" \
	  -X POST http://localhost:$(PORT)/predict/pregame \
	  -H "Content-Type: application/json" \
	  -H "X-API-Key: $(API_KEY)" \
	  -d '{"team1":{"team_name":"G2 Esports","side":"Blue","players":[ \
	         {"player":"BrokenBlade","champion":"K'\''Sante","position":"top"}, \
	         {"player":"Yike","champion":"Vi","position":"jng"}, \
	         {"player":"Caps","champion":"Azir","position":"mid"}, \
	         {"player":"Hans Sama","champion":"Varus","position":"bot"}, \
	         {"player":"Mikyx","champion":"Zyra","position":"sup"}]}, \
	       "team2":{"team_name":"MAD Lions KOI","side":"Red","players":[ \
	         {"player":"Myrwn","champion":"Gwen","position":"top"}, \
	         {"player":"Elyoya","champion":"Viego","position":"jng"}, \
	         {"player":"Fresskowy","champion":"Neeko","position":"mid"}, \
	         {"player":"Supa","champion":"Ashe","position":"bot"}, \
	         {"player":"Alvaro","champion":"Renata Glasc","position":"sup"}]}}') \
	|| { echo "ERROR: No se puede conectar a http://localhost:$(PORT)"; rm -f "$$tmp"; exit 1; }; \
	python3 -m json.tool < "$$tmp" 2>/dev/null || cat "$$tmp"; \
	rm -f "$$tmp"; \
	[ "$$status" -ge 200 ] && [ "$$status" -lt 300 ] \
	|| (echo "ERROR: HTTP $$status" && exit 1)

# ══════════════════════════════════════════════
# LIMPIEZA
# ══════════════════════════════════════════════
clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.parquet data/predictions.jsonl
	rm -f logs/*.log
	@echo "✓ Limpieza completa"

.PHONY: help setup dvc \
        start stop restart \
        start-all stop-all restart-all \
        test health \
        docker-build docker-up docker-down docker-test logs \
        train pipeline \
        predict predict-pregame \
        clean