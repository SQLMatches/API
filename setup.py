import os
import re

from setuptools import setup


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def get_variable(variable):
    with open(os.path.join("SQLMatches", "__init__.py")) as f:
        return re.search(
            "{} = ['\"]([^'\"]+)['\"]".format(variable), f.read()
        ).group(1)


setup(
    name="SQLMatches",
    version=get_variable("__version__"),
    url=get_variable("__url__"),
    description=get_variable("__description__"),
    author=get_variable("__author__"),
    author_email=get_variable("__author_email__"),
    install_requires=get_requirements(),
    license=get_variable("__license__"),
    packages=[
        "SQLMatches",
        "SQLMatches.api",
        "SQLMatches.community",
        "SQLMatches.routes"
    ],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False
)
