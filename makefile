.ONESHELL:

PYTHON_SOURCE_FILES = ./instance ./tests operations_engineering_landing_page.py ./landing_page_app

help:
	@echo "Available commands:"
	@echo "make setup            - Setup the environment"
	@echo "make test             - Run tests"
	@echo "make local            - Run application locally"

setup:
	python3 -m venv venv
	@venv/bin/pip3 install --upgrade pip
	@venv/bin/pip3 install -r requirements.txt

venv: requirements.txt
	python3 -m venv venv
	@venv/bin/pip3 install --upgrade pip
	@venv/bin/pip3 install -r requirements.txt

lint: venv
	pip install flake8
	pip install mypy
	pip install pylint
	@venv/bin/flake8 --ignore=E501,W503,E302 $(PYTHON_SOURCE_FILES)
	@venv/bin/mypy --ignore-missing-imports $(PYTHON_SOURCE_FILES)
	@venv/bin/pylint --recursive=y $(PYTHON_SOURCE_FILES)

format: venv
	pip install black
	@venv/bin/black $(PYTHON_SOURCE_FILES)

test:
	pip install coverage
	export FLASK_CONFIGURATION=development; coverage run -m unittest discover

test_and_report:
	coverage html && open htmlcov/index.html

clean-test:
	rm -fr venv
	rm -fr .tox/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

local: venv
	python3 operations_engineering_landing_page.py

all:

.PHONY: setup venv lint test format clean-test all
