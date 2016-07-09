GOOGLE_SPREADSHEET_ID ?= "fakeyfakeyfakey"
JIRA_URL ?= "http://localhost"
pytest_invoke = py.test -s --flake8 --cov=dashboard ./dashboard

venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

test: reqs
	GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) JIRA_URL=$(JIRA_URL) ./venv/bin/$(pytest_invoke)

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;

clean: clean_pycs
	rm -rf venv

docs: reqs
	cd docs && make html

up:
	docker-compose rm --all
	docker-compose up

test_docker:
	docker-compose build web
	docker-compose run -e GOOGLE_SPREADSHEET_ID=$(GOOGLE_SPREADSHEET_ID) -e JIRA_URL=$(JIRA_URL) web /app-ve/bin/$(pytest_invoke)

.PHONY: test clean clean_pycs docs climate test_docker
