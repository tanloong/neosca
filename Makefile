.PHONY: build run clean install lint test

build:
	python -m build
	pyinstaller ./utils/ns_packaging.spec --noconfirm --clean

run:
	./dist/neosca-gui/neosca-gui

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
	echo > src/neosca/ns_data/settings.ini
	pip install .

lint:
	ruff format src/ tests/
	ruff check src/ tests/
	mypy --check-untyped-defs src/

test:
	python -m unittest

ACKNOWLEDGMENTS.md: src/neosca/ns_data/acks.json utils/ns_generate_acks.py
	python utils/ns_generate_acks.py
