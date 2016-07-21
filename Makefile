GOOGLE_SPREADSHEET_ID ?= "fakeyfakeyfakey"
JIRA_URL ?= "http://localhost"
pytest_invoke = py.test -vvs --flake8 --cov=dashboard ./dashboard
DOCKER_IMAGE_NAME = "cmheisel/project-status-dashboard"
DOCKER_IMAGE_VERSION = $(shell cat dashboard/static/dashboard/version.txt)

venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

test: reqs
	DB_NAME=":memory:" GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) JIRA_URL=$(JIRA_URL) ./venv/bin/$(pytest_invoke)

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;

clean_db:
	rm -f data/*.db
	rm -f *.db

clean: clean_pycs
	rm -rf venv
	rm -rf static

docs: reqs
	cd docs && make html

up:
	docker-compose rm -f --all
	docker-compose build
	docker-compose up

clean_docker:
	docker-compose rm -f --all
	docker rmi projectstatusdashboard_web

test_docker:
	docker-compose build web
	docker-compose run -e GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) -e JIRA_URL=$(JIRA_URL) web /app-ve/bin/$(pytest_invoke)

release: test_docker clean clean_db clean_docker
	docker-compose build web
	docker tag projectstatusdashboard_web:latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)
	docker tag projectstatusdashboard_web:latest $(DOCKER_IMAGE_NAME):latest
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)
	docker push $(DOCKER_IMAGE_NAME):latest


.PHONY: test clean_pycs clean_db clean docs up clean_docker test_docker release
