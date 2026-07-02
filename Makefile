PYTHON ?= python3
QUARTO ?= quarto

.PHONY: all generate validate render clean seals

all: generate validate render

generate:
	$(PYTHON) scripts/bootstrap_project.py

validate:
	$(PYTHON) scripts/validate_data.py

seals:
	$(PYTHON) scripts/generate_seals.py

render:
	$(QUARTO) render

clean:
	rm -rf _site .quarto

