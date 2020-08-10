import setuptools


with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as req:
    requirements = req.read().split('\n')

setuptools.setup(
    name="reg-tools",
    version="0.0.1",
    author="Ruben Natvik",
    author_email="ronatvik@gmail.com",
    description="A package containing various regulation tools.",
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