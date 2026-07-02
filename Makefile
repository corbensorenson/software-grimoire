PYTHON ?= python3
QUARTO ?= quarto

.PHONY: all generate validate bench render test clean seals

all: generate validate bench render test

generate:
	$(PYTHON) scripts/bootstrap_project.py

validate:
	$(PYTHON) scripts/validate_data.py

bench:
	$(PYTHON) scripts/run_execution_bench.py
	$(PYTHON) scripts/run_hardness_bench.py

seals:
	$(PYTHON) scripts/generate_seals.py

render:
	$(QUARTO) render

test:
	$(PYTHON) -m pytest

clean:
	rm -rf _site .quarto
