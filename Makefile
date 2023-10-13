.PHONY: build run clean

build:
	pyinstaller ./neosca-gui.spec --noconfirm

run:
	./dist/neosca-gui/neosca-gui

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf neosca-gui.egg-info
	rm -rf htmlcov
	rm -rf coverage.xml
