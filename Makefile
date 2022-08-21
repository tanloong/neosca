.PHONY: clean build release install

clean:
	rm -rf build dist nl2sca.egg-info 

build: clean
	python setup.py sdist --formats=zip

release: build
	twine upload --repository testpypi dist/*

install: build
	sudo python setup.py install
