PYTHON ?= python3
CONTRACT_SCRIPT := scripts/check_weather_notebook_contracts.py

.PHONY: clean lint test build verify check

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(CONTRACT_SCRIPT)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(CONTRACT_SCRIPT)

build:
	@echo "Notebook project: no build artifact to compile."

verify: lint test build

check: clean verify
	$(MAKE) clean
