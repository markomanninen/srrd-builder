#!/usr/bin/env python3
"""
SRRD-Builder Package Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Scientific Research Requirement Document Builder"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    # Minimal requirements for CLI functionality
    requirements = [
        "click>=8.0.0",
        "pathlib",
        "argparse"
    ]

setup(
    name="srrd-builder",
    version="0.1.0",
    author="SRRD-Builder Team",
    author_email="contact@srrd-builder.org",
    description="Scientific Research Requirement Document Builder with MCP server integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markomanninen/srrd-builder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "srrd=srrd_builder.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "srrd_builder": [
            "config/*.json",
            "templates/**/*",
        ],
    },
    zip_safe=False,
)
