.PHONY: clean build release install

clean:
	rm -rf build
	rm -rf dist
	rm -rf nl2sca.egg-info
	pip uninstall -y nl2sca

build:
	python setup.py sdist bdist_wheel

release: build
	twine upload dist/*

install: build
	sudo python setup.py install
