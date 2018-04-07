GOOGLE_SPREADSHEET_ID ?= "fakeyfakeyfakey"
JIRA_URL ?= "http://localhost"
pytest_invoke = py.test -vvs --flake8 --cov-report html --cov=dashboard ./dashboard
DOCKER_IMAGE_NAME = "cmheisel/project-status-dashboard"
DOCKER_IMAGE_VERSION = $(shell cat dashboard/static/dashboard/version.txt)
VENV_BIN ?= ./venv/bin/

venv:
	virtualenv ./venv

reqs: venv 
	cd dashboard/static/dashboard && npm install
	$(VENV_BIN)pip install -r requirements.txt && touch reqs

.PHONY: test
test: reqs
	rm -rf static
	$(VENV_BIN)python ./manage.py collectstatic --noinput
	DB_NAME=":memory:" GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) JIRA_URL=$(JIRA_URL) $(VENV_BIN)$(pytest_invoke)

.PHONY: clean_pycs
clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \; || true
	find . -name "__pycache__" -exec rm -rf {} \; || true

.PHONY: clean_db
clean_db:
	rm -f data/*.db
	rm -f *.db

.PHONY: clean
clean: clean_pycs
	rm -rf reqs
	rm -rf venv
	rm -rf static
	rm -rf container/*.db
	rm -rf htmlcov

venv/bin/mkdocs: venv
	$(VENV_BIN)pip install -r requirements-docs.txt

.PHONY: docs
docs: reqs venv/bin/mkdocs
	$(VENV_BIN)mkdocs build -s

.PHONY: up
up:
	docker-compose rm -f --all
	docker-compose build
	docker-compose up

.PHONY: enter
enter:
	docker-compose rm -f
	docker-compose build
	docker run -ti projectstatusdashboard_web /bin/bash

.PHONY: clean_docker
clean_docker:
	docker-compose rm -f --all
	docker rmi projectstatusdashboard_web || true

.PHONY: test_docker
test_docker: clean clean_docker
	docker-compose build web
	docker-compose run -e DB_NAME=":memory:" -e GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) -e JIRA_URL=$(JIRA_URL) web /app/run.sh /app-ve/bin/$(pytest_invoke)

.PHONY: release
release: test_docker clean
	docker-compose build web
	docker tag projectstatusdashboard_web:latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)
	docker tag projectstatusdashboard_web:latest $(DOCKER_IMAGE_NAME):latest
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)
	docker push $(DOCKER_IMAGE_NAME):latest

.PHONY: publish_docs
publish_docs: docs
	$(VENV_BIN)mkdocs gh-deploy