.PHONY: all install build run clean clean-all

# Load .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Configuration
HF_MODEL_REPO ?= sauce-hug/korean-license-plate-detector
CACHE_DIR := .cache

# Directories
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python
BUILD_DIR := build
DIST_DIR := dist

# Source directory
SRC_DIR := src

# Detect OS
UNAME_S := $(shell uname -s)

all: build

venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt

download-models: install
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); from utils.model_loader import download_all_models; download_all_models()"

build: install download-models
	@echo "Building for $(UNAME_S)..."
	@echo "Model repo: $(HF_MODEL_REPO)"
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -m PyInstaller korean-license-plate-detector.spec --noconfirm
	@echo ""
	@echo "Build complete: $(DIST_DIR)/korean-license-plate-detector/"

run: install
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		cd $(SRC_DIR) && $(PYTHON) widget.py

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(CACHE_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	rm -rf $(VENV)

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      - Build executable (downloads models if needed)"
	@echo "  run        - Run the app"
	@echo "  clean      - Remove build artifacts and cache"
	@echo "  clean-all  - Remove venv and all build artifacts"
	@echo ""
	@echo "Configuration:"
	@echo "  HF_MODEL_REPO=$(HF_MODEL_REPO)"
