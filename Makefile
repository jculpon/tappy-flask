help:
	@echo 'Usage:'
	@echo '   make deps       installs dependencies'
	@echo '   make db         sets up the development database'
	@echo '   make devserver  starts the development server'
	@echo '   make test       run the tests'
	@echo '   make clean      removes compiled files'
	@echo '   make help       displays this message'

deps:
	pip install -r requirements.txt

devserver: tappy.db
	python tappy.py

test: db
	python tappy_tests.py

clean:
	find . -name '*.py[co]' -exec rm -f {} \;
	rm -f tappy.db

db: tappy.db

tappy.db: schema.sql hope.sql
	python -c 'from tappy import init_flask_db; init_flask_db()'

.PHONY: help deps clean test devserver db
