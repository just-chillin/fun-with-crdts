VENV := .venv
PYTHON := $(VENV)/bin/python

$(VENV):
	python3 -m venv $(VENV)

.PHONY: client
client: $(VENV)
	$(PYTHON) client.py

server: $(VENV)
	$(PYTHON) server.py