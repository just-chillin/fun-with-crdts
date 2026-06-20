VENV := .venv
PYTHON := $(VENV)/bin/python

$(VENV):
	python3 -m venv $(VENV)

.PHONY: run
run: $(VENV)
	$(PYTHON) main.py