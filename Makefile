GOOGLE_SPREADSHEET_ID ?= "fakeyfakeyfakey"
JIRA_URL ?= "http://localhost"

venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

test: reqs
	GOOGLE_SPREADSHEET_ID=$GOOGLE_SPREADSHEET_ID JIRA_URL=$JIRA_URL ./venv/bin/py.test -svv --flake8 --cov=dashboard ./dashboard

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;

clean: clean_pycs
	rm -rf venv

docs: reqs
	cd docs && make html


.PHONY: test clean clean_pycs docs climate
