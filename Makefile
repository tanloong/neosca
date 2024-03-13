.PHONY: build clean install lint run test

build:
	python -m build
	pyinstaller ./utils/ns_packaging.spec --noconfirm --clean

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf coverage.xml
	rm -rf build/
	rm -rf dist/
	rm -rf src/neosca.egg-info

install:
	# avoid rm
	echo > src/neosca/ns_data/settings.ini
	pip install .

lint:
	ruff format src/ tests/
	ruff check src/ tests/
	mypy --check-untyped-defs src/

test:
	python -m unittest

run:
	cd ./src && python -m neosca gui

ACKNOWLEDGMENTS.md: src/neosca/ns_data/acks.json utils/ns_generate_acks.py
	python utils/ns_generate_acks.py
