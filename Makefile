help:
	@echo 'Usage:'
	@echo '   make deps       installs dependencies'
	@echo '   make devserver  starts the development server'
	@echo '   make test       run the tests'
	@echo '   make clean      removes compiled files'
	@echo '   make help       displays this message'

deps:
	pip install -r requirements.txt

devserver:
	python tappy.py

test:
	python tappy_tests.py

clean:
	find . -name '*.py[co]' -exec rm -f {} \;

.PHONY: help deps clean
