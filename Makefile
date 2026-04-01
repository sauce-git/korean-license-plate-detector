.PHONY: all install build run run-debug test clean clean-all help

# Load .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Configuration
HF_MODEL_REPO ?= sauce-hug/korean-license-plate-detector
CACHE_DIR := .cache
PYTHON_VERSION := 3.11.9
PYTHON_BUILD_DATE := 20240726

# Directories
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python
BUILD_DIR := build
DIST_DIR := dist
TOOLS_DIR := .tools

# Source directory
SRC_DIR := src
PKG_NAME := klpd

# Detect OS and architecture
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Determine Python standalone download URL
ifeq ($(UNAME_S),Darwin)
    ifeq ($(UNAME_M),arm64)
        PYTHON_ARCH := aarch64-apple-darwin
        PYTHON_EXT := tar.gz
    else
        PYTHON_ARCH := x86_64-apple-darwin
        PYTHON_EXT := tar.gz
    endif
else ifeq ($(UNAME_S),Linux)
    PYTHON_ARCH := x86_64-unknown-linux-gnu
    PYTHON_EXT := tar.gz
endif

PYTHON_BASE_URL := https://github.com/indygreg/python-build-standalone/releases/download/$(PYTHON_BUILD_DATE)
PYTHON_FILE := cpython-$(PYTHON_VERSION)+$(PYTHON_BUILD_DATE)-$(PYTHON_ARCH)-install_only
PYTHON_URL := $(PYTHON_BASE_URL)/$(PYTHON_FILE).$(PYTHON_EXT)
PYTHON_BIN := $(TOOLS_DIR)/python/bin/python3

all: build

# Download and extract Python standalone
$(TOOLS_DIR)/python/bin/python3:
	@echo "Downloading Python $(PYTHON_VERSION) for $(UNAME_S) $(UNAME_M)..."
	@mkdir -p $(TOOLS_DIR)
	@curl -sL "$(PYTHON_URL)" -o "$(TOOLS_DIR)/python.$(PYTHON_EXT)"
	@mkdir -p $(TOOLS_DIR)/python
	@tar -xzf "$(TOOLS_DIR)/python.$(PYTHON_EXT)" -C "$(TOOLS_DIR)/python" --strip-components=1
	@rm "$(TOOLS_DIR)/python.$(PYTHON_EXT)"
	@echo "Python installed to $(TOOLS_DIR)/python/bin/python3"
	@$(PYTHON_BIN) --version

venv: $(PYTHON_BIN)
	@echo "Creating virtual environment..."
	@$(PYTHON_BIN) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

download-models: install
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -c "from klpd.models import download_all_models; download_all_models()"

build: install download-models
	@echo "Building for $(UNAME_S)..."
	@echo "Model repo: $(HF_MODEL_REPO)"
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -m PyInstaller korean-license-plate-detector.spec --noconfirm
	@echo ""
	@echo "Build complete: $(DIST_DIR)/"
	@ls -la $(DIST_DIR)/

run: install
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -m klpd.cli

run-debug: install
	HF_MODEL_REPO=$(HF_MODEL_REPO) HF_MODEL_CACHE=$(CACHE_DIR) \
		$(PYTHON) -m klpd.cli --debug

test: install
	@echo "Checking for pytest..."
	@$(PYTHON) -m pip install pytest -q
	$(PYTHON) -m pytest tests/ -v

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(CACHE_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	rm -rf $(VENV) $(TOOLS_DIR)

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build       - Build executable (downloads Python and models if needed)"
	@echo "  run         - Run the app"
	@echo "  run-debug   - Run the app with debug mode enabled"
	@echo "  test        - Run tests"
	@echo "  clean       - Remove build artifacts and cache"
	@echo "  clean-all   - Remove venv, tools, and all build artifacts"
	@echo ""
	@echo "Configuration:"
	@echo "  HF_MODEL_REPO=$(HF_MODEL_REPO)"
	@echo "  PYTHON_VERSION=$(PYTHON_VERSION)"
