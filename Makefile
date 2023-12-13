.PHONY: build run clean lint

build:
	pyinstaller ./neosca-gui.spec --noconfirm

run:
	./dist/neosca-gui/neosca-gui

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf coverage.xml

lint:
	ruff format src/ tests/
	ruff check src/ tests/
	mypy --check-untyped-defs src/
