PYTHON ?= python3
QUARTO ?= quarto

.PHONY: all generate validate render test clean seals

all: generate validate render test

generate:
	$(PYTHON) scripts/bootstrap_project.py

validate:
	$(PYTHON) scripts/validate_data.py

seals:
	$(PYTHON) scripts/generate_seals.py

render:
	$(QUARTO) render

test:
	$(PYTHON) -m pytest

clean:
	rm -rf _site .quarto
