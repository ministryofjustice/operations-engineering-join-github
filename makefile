.ONESHELL:

PYTHON_SOURCE_FILES = ./tests operations_engineering_join_github.py ./join_github_app
# Default values for variables (can be overridden by passing arguments to `make`)
RELEASE_NAME ?= default-release-name
AUTH0_CLIENT_ID ?= default-auth0-client-id
AUTH0_CLIENT_SECRET ?= default-auth0-client-secret
APP_SECRET_KEY ?= default-app-secret-key
ENCRYPTION_KEY ?= default-encryption-key
API_KEY ?= default-api-key
HOST_SUFFIX ?= default-host-suffix
IMAGE ?= default-image
REGISTRY ?= default-registry

help:
	@echo "Available commands:"
	@echo "make venv             - venv the environment"
	@echo "make test             - Run tests"
	@echo "make local            - Run application locally"
	@echo "make lint             - Run Lint tools"
	@echo "make report           - Open the Code Coverage report"

venv: requirements.txt
	python3 -m venv venv .venv
	venv/bin/pip3 install --upgrade pip
	venv/bin/pip3 install -r requirements.txt

# Run MegaLinter
lint:
	npx mega-linter-runner -e 'SHOW_ELAPSED_TIME=true'

format: venv
	venv/bin/pip3 install black
	venv/bin/black $(PYTHON_SOURCE_FILES)

test: venv
	venv/bin/pip3 install pytest
	venv/bin/pip3 install coverage
	export FLASK_CONFIGURATION=development; venv/bin/coverage run -m pytest tests/ -v

report:
	venv/bin/coverage html && open htmlcov/index.html

clean-test:
	rm -fr venv
	rm -fr .venv
	rm -fr .tox/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .coverage
	rm -fr htmlcov/

local: venv
	export FLASK_CONFIGURATION=development; venv/bin/python3 -m operations_engineering_join_github

# Assumes you've already built the image locally
docker-up:
	docker-compose -f docker-compose.yaml up -d

# To run locally, you need to pass the following:
# make deploy-dev IMAGE=my-image RELEASE_NAME=my-release AUTH0_CLIENT_ID=my-auth0-id AUTH0_CLIENT_SECRET=my-secret APP_SECRET_KEY=my-app-secret HOST_NAME=my-host
deploy-dev:
	helm --debug upgrade join-github helm/join-github \
		--install \
		--force \
		--wait \
		--set image.tag=$(IMAGE) \
		--set application.auth0ClientId=$(AUTH0_CLIENT_ID) \
		--set application.auth0ClientSecret=$(AUTH0_CLIENT_SECRET) \
		--set application.appSecretKey=$(APP_SECRET_KEY) \
		--set application.apiKey=$(API_KEY) \
		--set ingress.hosts={$(HOST_NAME).cloud-platform.service.justice.gov.uk} \
		--set image.repository=754256621582.dkr.ecr.eu-west-2.amazonaws.com/operations-engineering/operations-engineering-join-github-dev-ecr \
		--namespace operations-engineering-join-github-dev

all:

.PHONY: venv lint test format local clean-test report all
