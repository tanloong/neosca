.PHONY: build package clean install lint run test bump

build: clean acks
	python3 -m build

package: clean acks model
	python3 ./utils/ns_packaging.py

model: requirements.txt
	python3 -m utils.ns_download_models

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf coverage.xml
	rm -rf build/
	rm -rf dist/
	rm -rf src/neosca.egg-info
	# delete macos metadata
	find src/neosca/ns_data/ -name "._*" -type f -delete
	find src/neosca/ns_data/ -name ".DS_Store" -type f -delete

install:
	# avoid rm
	echo > src/neosca/ns_data/settings.ini
	pip install .

lint:
	ruff format src/ tests/
	ruff check src/ tests/ --fix
	mypy --check-untyped-defs src/

test:
	python3 -m unittest

run:
	cd ./src && python3 -m neosca gui

acks: src/neosca/ns_data/acks.json utils/ns_generate_acks.py
	python3 ./utils/ns_generate_acks.py

component="patch"
bump:
	# make bump
	# make bump component=patch
	# make bump component=minor
	# make bump component=major
	bash ./utils/ns_bump_version.sh $(component)
