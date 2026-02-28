from setuptools import setup, find_packages

from tds_up import __version__

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip()]

setup(
    name="3ds-up",
    version=__version__,
    description="Actualizador seguro de Nintendo 3DS para macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Oscar Campohermoso",
    license="GPLv3",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "3ds-up=tds_up.cli:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Topic :: Utilities",
    ],
)
