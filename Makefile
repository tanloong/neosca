.PHONY: clean build release install

clean:
	rm -rf build
	rm -rf dist
	rm -rf nl2sca.egg-info
	pip uninstall -y nl2sca

build:
	python setup.py sdist bdist_wheel

release:
	twine upload dist/*

	sudo python setup.py install
install:
