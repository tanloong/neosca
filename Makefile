.PHONY: refresh clean build release install

refresh: clean build install

clean:
	rm -rf __pychache__
	rm -rf tests/__pychache__
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
