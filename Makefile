SHELL := /bin/bash

BACKEND_DIR := backend
FRONTEND_DIR := frontend
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 3000

.PHONY: help install install-backend install-frontend backend frontend serve

help:
	@echo "Targets:"
	@echo "  make install           Install backend + frontend dependencies"
	@echo "  make backend           Run backend server (uvicorn)"
	@echo "  make frontend          Run frontend dev server (Next.js)"
	@echo "  make serve             Run backend + frontend together"
	@echo ""
	@echo "Optional overrides:"
	@echo "  BACKEND_PORT=8000 FRONTEND_PORT=3000"

install: install-backend install-frontend

install-backend:
	cd $(BACKEND_DIR) && pip install -r requirements.txt

install-frontend:
	cd $(FRONTEND_DIR) && npm install

backend:
	cd $(BACKEND_DIR) && uvicorn app:app --reload --port $(BACKEND_PORT)

frontend:
	cd $(FRONTEND_DIR) && PORT=$(FRONTEND_PORT) npm run dev

serve:
	@echo "Starting backend on :$(BACKEND_PORT) and frontend on :$(FRONTEND_PORT)"
	@set -euo pipefail; \
	BACKEND_PID=""; FRONTEND_PID=""; \
	trap 'echo ""; echo "Stopping servers..."; [ -n "$$BACKEND_PID" ] && kill $$BACKEND_PID >/dev/null 2>&1 || true; [ -n "$$FRONTEND_PID" ] && kill $$FRONTEND_PID >/dev/null 2>&1 || true' INT TERM EXIT; \
	$(MAKE) --no-print-directory backend & BACKEND_PID=$$!; \
	$(MAKE) --no-print-directory frontend & FRONTEND_PID=$$!; \
	wait $$BACKEND_PID $$FRONTEND_PID
