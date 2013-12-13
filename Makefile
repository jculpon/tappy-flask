help:
	@echo 'Usage:'
	@echo '   make deps    installs dependencies'
	@echo '   make clean   removes compiled files'
	@echo '   make help    displays this message'

deps:
	pip install -r requirements.txt

clean:
	find . -name '*.py[co]' -exec rm -f {} \;

.PHONY: help deps clean
