.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check clean lint lock root-test test verify
.SECONDEXPANSION:

PYTHON ?= python3
override PYTHON := $(value PYTHON)
export PYTHON
UV ?= uv
override UV := $(value UV)
export UV
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value PYTHON)),)
$(error PYTHON must be a literal executable path, not Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value UV)),)
$(error UV must be a literal executable path, not Make syntax)
endif
override SHELL := /bin/sh
override .SHELLFLAGS := -c
build check clean lint lock root-test test verify __repository-make-authority: override SHELL := /bin/sh
build check clean lint lock root-test test verify __repository-make-authority: override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
override REPOSITORY_SHELL_LITERAL = $(subst $$,$$$$,$(subst ','"'"',$1))
override REPOSITORY_ROOT_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(ROOT))
override REPOSITORY_PYTHON_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(PYTHON))
override REPOSITORY_UV_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(UV))

build check clean lint lock root-test test verify:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check clean lint lock root-test test verify:: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | /usr/bin/sed 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check clean lint lock root-test test verify:: __repository-make-authority

__repository-make-authority::
	@:

define REPOSITORY_PUBLIC_RECIPES
clean::
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +

lint::
	PYTHONDONTWRITEBYTECODE=1 '$(REPOSITORY_PYTHON_LITERAL)' -m py_compile '$(REPOSITORY_ROOT_LITERAL)/weather_notebook.py' '$(REPOSITORY_ROOT_LITERAL)/weather_notebook_tests.py' '$(REPOSITORY_ROOT_LITERAL)/scripts/check_weather_notebook_contracts.py'

lock::
	'$(REPOSITORY_UV_LITERAL)' pip compile '$(REPOSITORY_ROOT_LITERAL)/requirements.txt' --python-version 3.12 --python-platform x86_64-manylinux_2_28 --default-index https://pypi.org/simple --generate-hashes --custom-compile-command 'make lock' --output-file '$(REPOSITORY_ROOT_LITERAL)/requirements-py312.lock'
	'$(REPOSITORY_UV_LITERAL)' pip compile '$(REPOSITORY_ROOT_LITERAL)/requirements.txt' --python-version 3.14 --python-platform x86_64-manylinux_2_28 --default-index https://pypi.org/simple --generate-hashes --custom-compile-command 'make lock' --output-file '$(REPOSITORY_ROOT_LITERAL)/requirements-py314.lock'

test::
	PYTHONPATH='$(REPOSITORY_ROOT_LITERAL)' PYTHONDONTWRITEBYTECODE=1 '$(REPOSITORY_PYTHON_LITERAL)' -m unittest weather_notebook_tests
	PYTHONDONTWRITEBYTECODE=1 '$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/check_weather_notebook_contracts.py'

build::
	@/usr/bin/printf '%s\n' 'Notebook project: no build artifact to compile.'

root-test::
	/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'

verify:: root-test lint test build

check:: clean verify
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +
endef

$(eval $(REPOSITORY_PUBLIC_RECIPES))
