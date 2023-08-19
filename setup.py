import setuptools

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("./neosca/about.py", "r", encoding="utf-8") as f:
    about = {}
    exec(f.read(), about)

setuptools.setup(
    name="neosca",
    version=about["__version__"],
    author="Long Tan",
    author_email="tanloong@foxmail.com",
    url="https://github.com/tanloong/neosca",
    packages=["neosca", "neosca.lca"],
    package_data={
        "neosca": [
            "data/structure_data.json",
            "data/anc_all_count.pickle.lzma",
            "data/bnc_all_filtered.pickle.lzma",
        ]
    },
    description="Another syntactic complexity analyzer of written English language samples",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["JPype1", "charset-normalizer"],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["nsca = neosca:main", "nsca-lca = neosca:lca_main", "nsca-tregex = neosca:tregex_cli"]},
)
