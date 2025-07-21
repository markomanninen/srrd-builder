#!/usr/bin/env python3
"""
SRRD-Builder Package Setup - Global Installation Support
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
if (readme_file.exists()):
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Scientific Research Requirement Document Builder with AI-powered MCP server"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if (requirements_file.exists()):
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    # Essential requirements for full functionality
    requirements = [
        "click>=8.0.0",
        "pathlib",
        "argparse",
        "websockets>=11.0.0",
        "sqlite3",
        "GitPython>=3.1.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "numpy>=1.26.0",  # Updated for Python 3.12 compatibility
        "asyncio"
    ]

# Optional requirements for enhanced functionality  
extras_require = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=1.0.0"
    ],
    "latex": [
        "pylatex>=1.4.0",
        "bibtexparser>=1.4.0"
    ],
    "ml": [
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "scikit-learn>=1.1.0"
    ],
    "all": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0", 
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=1.0.0",
        "pylatex>=1.4.0",
        "bibtexparser>=1.4.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "scikit-learn>=1.1.0"
    ]
}

setup(
    name="srrd-builder",
    version="1.0.0",
    author="SRRD-Builder Team", 
    author_email="contact@srrd-builder.org",
    description="Scientific Research Requirement Document Builder with AI-powered MCP server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markomanninen/srrd-builder",
    project_urls={
        "Bug Tracker": "https://github.com/markomanninen/srrd-builder/issues",
        "Documentation": "https://github.com/markomanninen/srrd-builder/blob/main/README.md",
        "Source Code": "https://github.com/markomanninen/srrd-builder"
    },
    packages=find_packages(include=['srrd_builder', 'srrd_builder.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education", 
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Framework :: AsyncIO"
    ],
    keywords="research, scientific, latex, mcp, ai, document-generation, collaboration",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "srrd=srrd_builder.cli.main:main",
            "srrd-server=srrd_builder.server.launcher:main",
        ],
    },
    include_package_data=True,
    package_data={
        "srrd_builder": [
            "config/*.json",
            "config/*.sql", 
            "templates/**/*",
            "work/code/mcp/**/*",
            "work/docs/**/*"
        ],
    },
    data_files=[
        ("share/srrd-builder/config", ["work/code/mcp/config/database_schema.sql"]),
        ("share/srrd-builder/templates", ["work/docs/templates/RESEARCH_TEMPLATES.md"]),
    ],
    zip_safe=False,
)
