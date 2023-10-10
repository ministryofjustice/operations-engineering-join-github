.ONESHELL:

# Default values for variables (can be overridden by passing arguments to `make`)
PYTHON_SOURCE_FILES = ./instance ./landing_page_app ./tests setup.py operations_engineering_landing_page.py build.py
RELEASE_NAME ?= default-release-name
APP_SECRET_KEY ?= default-app-secret-key
HOST_SUFFIX ?= default-host-suffix
IMAGE ?= default-image
REGISTRY ?= default-registry

# Targets
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
	@venv/bin/flake8 --ignore=E501,W503 $(PYTHON_SOURCE_FILES)
	@venv/bin/mypy --ignore-missing-imports $(PYTHON_SOURCE_FILES)
	@venv/bin/pylint --recursive=y $(PYTHON_SOURCE_FILES)

format: venv
	@venv/bin/black $(PYTHON_SOURCE_FILES)

test:
	export FLASK_CONFIGURATION=development; python3 -m pytest -v

clean-test:
	rm -fr venv
	rm -fr .tox/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

# To deploy, you need to pass the following:
# make deploy IMAGE=my-image RELEASE_NAME=my-release APP_SECRET_KEY=my-app-secret HOST_SUFFIX=my-host-suffix
# deploy-dev:
# 	helm --debug upgrade $(RELEASE_NAME) helm/operations-engineering-landing-page \
# 		--install \
# 		--force \
# 		--wait \
# 		--set image.tag=$(IMAGE) \
# 		--set application.appSecretKey=$(APP_SECRET_KEY) \
# 		--set ingress.hosts={operations-engineering-landing-page-poc-$(HOST_SUFFIX).cloud-platform.service.justice.gov.uk} \
# 		--set image.repository=754256621582.dkr.ecr.eu-west-2.amazonaws.com/operations-engineering/operations-engineering-landing-page-poc-ecr \
# 		--namespace operations-engineering-landing-page-poc

# delete-dev:
# 	helm delete $(RELEASE_NAME) --namespace operations-engineering-landing-page-poc

local: venv
	python3 operations_engineering_landing_page.py

all:

.PHONY: setup venv lint test format clean-test all
