from distutils.core import setup

with open('./README.md') as f:
    long_description = f.read()
with open('./nl2sca/__init__.py') as f:
    for line in f.readlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            version = line.split(delim)[1]
            break
    else:
        print("Can't find version! Stop Here!")
        exit(1)
setup(
    name="nl2sca",
    version=version,
    author="TAN Long",
    author_email="tanloong@foxmail.com",
    url="https://github.com/tanloong/NeoL2SCA",
    packages=["nl2sca", "nl2sca.utils", "nl2sca.samples"],
    description="NeoL2SCA is a rewrite of Xiaofei Lu's L2 Syntactic Complexity Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 or later"
        " (GPLv2+)",
    ],
)
