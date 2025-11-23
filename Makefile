.DEFAULT_GOAL := figures

PYTHON ?= python3

.PHONY: figures clean

# Generate fresh inflation figures (SVG) into ./output
figures:
	$(PYTHON) main.py

# Remove generated artifacts
clean:
	rm -rf output
