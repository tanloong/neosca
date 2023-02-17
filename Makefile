.PHONY: refresh clean build release install test lint

refresh: lint clean build install

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf build
	rm -rf dist
	rm -rf neosca.egg-info
	rm -rf htmlcov
	rm -rf coverage.xml
	pip uninstall -y neosca

build:
	python setup.py sdist bdist_wheel

release:
	python -m twine upload dist/*

install:
	python setup.py install --user

test:
	python -m unittest

lint:
	autopep8 neosca/ tests/ --in-place --recursive --max-line-length 97
	flake8 neosca/ tests/ --count --max-line-length=97 --statistics
	mypy --check-untyped-defs neosca/
