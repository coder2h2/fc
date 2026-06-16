from setuptools import setup, find_packages

setup(
    name="fc",
    version="1.0.0",
    description="FileConnect (fc) - Links Python files to all related file types in the project",
    author="ip-ascii",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
