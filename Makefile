.PHONY: build package clean install lint run test bump freeze

build: clean acks
	python -m build

package: clean acks model
	python ./scripts/ns_packaging.py

model: requirements.txt
	python -m scripts.ns_download_models

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
	ruff check src/ tests/ --fix
	ruff format src/ tests/
	mypy --check-untyped-defs src/

test:
	python -m unittest

run:
	cd ./src && python -m neosca gui

acks: src/neosca/ns_data/acks.json scripts/ns_generate_acks.py
	python ./scripts/ns_generate_acks.py

component="patch"
bump:
	# make bump
	# make bump component=patch
	# make bump component=minor
	# make bump component=major
	bash ./scripts/ns_bump_version.sh $(component)

freeze:
	bash ./scripts/ns_freeze.sh

sync:
	# unlisted packages will be removed
	uv pip sync ./requirements.txt
	# install missing intermediate dependencies
	uv pip install -r ./requirements.txt
