import setuptools


with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as req:
    requirements = req.read().split('\n')

setuptools.setup(
    name="dsp-module",
    version="0.0.2",
    author="Ruben Natvik",
    author_email="ronatvik@gmail.com",
    description="A module containing useful tools for digital signal processing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/RNatvik/rntools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)