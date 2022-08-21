from distutils.core import setup

setup(
    name="nl2sca",
    version="0.0.6",
    author="TAN Long",
    author_email="tanloong@foxmail.com",
    url="https://github.com/tanloong/NeoL2SCA",
    packages=["nl2sca", "nl2sca.utils", "nl2sca.samples"],
    description="New L2 Syntactic Complexity Analyzer",
    long_description=(
        "NeoL2SCA performs syntactic complexity analysis of written English"
        " language samples. It is a rewrite of"
        " [L2SCA](http://personal.psu.edu/xxl13/downloads/l2sca.html), with"
        " extended functionalities."
    ),
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 or later"
        " (GPLv2+)",
    ],
)
