.PHONY: install test lint status clean

install:
	pip install -e .

test:
	pytest tests/

lint:
	flake8 asdlc tests

status:
	asdlc status

clean:
	rm -rf build dist *.egg-info .pytest_cache __pycache__
