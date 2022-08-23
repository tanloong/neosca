from distutils.core import setup
from os import path

cur_dir = path.dirname(__file__)
readme = open(path.join(cur_dir,'README.md'),'r').read()
setup(
    name="nl2sca",
    version="0.0.13",
    author="TAN Long",
    author_email="tanloong@foxmail.com",
    url="https://github.com/tanloong/NeoL2SCA",
    packages=["nl2sca", "nl2sca.utils", "nl2sca.samples"],
    description="NeoL2SCA is a rewrite of Xiaofei Lu's L2 Syntactic Complexity Analyzer",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 or later"
        " (GPLv2+)",
    ],
)
