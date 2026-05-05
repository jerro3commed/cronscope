"""Setup configuration for cronscope."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cronscope",
    version="0.1.0",
    author="cronscope contributors",
    description="Lightweight utility to visualize and validate cron expressions with next-run previews in the terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/cronscope",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        # No external runtime dependencies — stdlib only
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cronscope=cronscope.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration",
    ],
    keywords="cron scheduler terminal cli preview validate",
)
