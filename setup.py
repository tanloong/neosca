import setuptools

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
with open("./neosca/__init__.py", "r", encoding="utf-8") as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            version = line.split(delim)[1]
            break
    else:
        print("Can't find version! Stop Here!")
        exit(1)
setuptools.setup(
    name="neosca",
    version=version,
    author="TAN Long",
    author_email="tanloong@foxmail.com",
    url="https://github.com/tanloong/neosca",
    packages=["neosca"],
    description="Another syntactic complexity analyzer of written English language samples",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['JPype1'],
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
    entry_points={"console_scripts": ["nsca = neosca:main"]},
)
