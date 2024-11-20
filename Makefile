VENV_BIN ?= python3 -m venv
VENV_DIR ?= .venv
PIP_CMD ?= pip3

ifeq ($(OS), Windows_NT)
	VENV_ACTIVATE = $(VENV_DIR)/Scripts/activate
else
	VENV_ACTIVATE = $(VENV_DIR)/bin/activate
endif

VENV_RUN = . $(VENV_ACTIVATE)


$(VENV_ACTIVATE): pyproject.toml
	test -d $(VENV_DIR) || $(VENV_BIN) $(VENV_DIR)
	$(VENV_RUN); $(PIP_CMD) install --upgrade pip setuptools wheel plux
	touch $(VENV_ACTIVATE)


venv: $(VENV_ACTIVATE)    ## Create a new (empty) virtual environment

format: venv           		  ## Run ruff and black to format the whole codebase
	($(VENV_RUN); python -m ruff check --output-format=full --fix .; python -m black .)

lint: venv      		  ## Run code linter to check code style and check if formatter would make changes
	($(VENV_RUN); python -m ruff check --show-source . && python -m black --check .)

install: venv
	$(VENV_RUN); $(PIP_CMD) install -e ".[test,dev]"

test: venv              	  ## Run tests
	($(VENV_RUN); python -m pytest -v --cov=plux --cov-report=term-missing --cov-report=xml tests)

