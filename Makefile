.PHONY: refresh clean build release install test cov lint

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

cov:
	python -m coverage run -m unittest
	python -m coverage html

lint:
	black neosca/ tests/ --line-length 97 --preview
	flake8 neosca/ tests/ --count --max-line-length=97 --statistics --ignore=E203,E501,W503
	mypy --check-untyped-defs neosca/

README_zh_tw.md: README_zh_cn.md
	cd ~/software/zhconv && python -m zhconv zh-tw < ~/projects/neosca/README_zh_cn.md > ~/projects/neosca/README_zh_tw.md
