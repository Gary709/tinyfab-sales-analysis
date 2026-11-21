.PHONY: all test

all:
	python3 analysis.py

test:
	python3 -m pytest -q
