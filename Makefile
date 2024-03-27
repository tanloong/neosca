.PHONY: build package clean install lint run test bump_version

build: clean ACKNOWLEDGMENTS.md
	python3 -m build

package: clean ACKNOWLEDGMENTS.md
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

ACKNOWLEDGMENTS.md: src/neosca/ns_data/acks.json utils/ns_generate_acks.py
	python3 utils/ns_generate_acks.py

component="patch"
bump_version:
	# make bump_version
	# make bump_version component=minor
	# make bump_version component=major
	bash ./utils/ns_bump_version.sh $(component)
