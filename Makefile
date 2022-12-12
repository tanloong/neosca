.PHONY: refresh clean build release install test

refresh: clean build install

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf build
	rm -rf dist
	rm -rf neosca.egg-info
	pip uninstall -y neosca

build:
	python setup.py sdist bdist_wheel

release:
	python -m twine upload dist/*

install:
	python setup.py install --user

test:
	python -m unittest
