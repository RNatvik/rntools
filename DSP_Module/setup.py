import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="dsp-module",
    version="0.0.1",
    author="Ruben Natvik",
    author_email="ronatvik@gmail.com",
    description="A framework for communication across separate python processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RNatvik/rntools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)