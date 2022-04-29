install:
	pip install .

test:
	pytest .

coverage:
	coverage run -m pytest .
	coverage report -m

lint:
	flake8 .
	mypy .
	codespell .

test-all: coverage lint
