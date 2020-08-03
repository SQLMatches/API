import os
import re

from setuptools import setup


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def get_version(package):
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search(
            "__version__ = ['\"]([^'\"]+)['\"]", f.read()
        ).group(1)


setup(
    name="SQLMatches",
    version=get_version("SQLMatches"),
    url="https://github.com/WardPearce/SQLMatches",
    description="SQLMatches is a free & open source software built around" +
        "giving players & communities easy access to match records & demos.",
    author="WardPearce",
    author_email="wardpearce@protonmail.com",
    install_requires=get_requirements(),
    license="GPL v3",
    packages=[
        "SQLMatches",
        "SQLMatches.api",
        "SQLMatches.community",
        "SQLMatches.forms",
        "SQLMatches.routes"
    ],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False
)
