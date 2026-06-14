PYTHON ?= python3
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CONTRACT_SCRIPT := $(ROOT)/scripts/check_weather_notebook_contracts.py
PYTHON_FILES := $(ROOT)/weather_notebook.py $(ROOT)/weather_notebook_tests.py $(CONTRACT_SCRIPT)

.PHONY: clean lint lock test build verify check

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

lock:
	cd "$(ROOT)" && uv pip compile requirements.txt --python-version 3.12 --python-platform x86_64-manylinux_2_28 --default-index https://pypi.org/simple --generate-hashes --custom-compile-command 'make lock' --output-file requirements-py312.lock
	cd "$(ROOT)" && uv pip compile requirements.txt --python-version 3.14 --python-platform x86_64-manylinux_2_28 --default-index https://pypi.org/simple --generate-hashes --custom-compile-command 'make lock' --output-file requirements-py314.lock

test:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest weather_notebook_tests
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(CONTRACT_SCRIPT)

build:
	@echo "Notebook project: no build artifact to compile."

verify: lint test build

check: clean verify
	$(MAKE) -C "$(ROOT)" clean
