PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CONTRACT_SCRIPT := $(ROOT)/scripts/check_weather_notebook_contracts.py
PYTHON_FILES := $(ROOT)/weather_notebook.py $(ROOT)/weather_notebook_tests.py $(CONTRACT_SCRIPT)

.PHONY: clean lint test build verify check

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

test:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest weather_notebook_tests
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(CONTRACT_SCRIPT)

build:
	@echo "Notebook project: no build artifact to compile."

verify: lint test build

check: clean verify
	$(MAKE) -C "$(ROOT)" clean
