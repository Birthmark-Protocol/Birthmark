"""
Setup configuration for Birthmark Protocol package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() 
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="birthmark-protocol",
    version="0.1.0",
    author="Samuel C. Ryan",
    author_email="samryan.pdx@proton.me",
    description="Permanent authentication for digital media through camera-native blockchain verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/birthmark-protocol/birthmark",
    project_urls={
        "Bug Tracker": "https://github.com/birthmark-protocol/birthmark/issues",
        "Documentation": "https://github.com/birthmark-protocol/birthmark/blob/main/README.md",
        "Source Code": "https://github.com/birthmark-protocol/birthmark",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "birthmark=birthmark.cli:main",  # CLI tool (to be implemented)
        ],
    },
    keywords="authentication blockchain cryptography deepfake verification camera photography",
    license="Apache-2.0",
)
