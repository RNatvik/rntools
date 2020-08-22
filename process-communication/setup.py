import setuptools


with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as req:
    requirements = req.read().split('\n')

setuptools.setup(
    name="process-communication",
    version="0.0.5",
    author="Ruben Natvik",
    author_email="ronatvik@gmail.com",
    description="A framework for communication across separate python processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/RNatvik/rntools",
    packages=setuptools.find_packages(exclude=('examples',)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)