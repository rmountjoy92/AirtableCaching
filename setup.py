import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airtable-caching",
    version="0.0.5",
    author="rmountjoy",
    author_email="ross.mountjoy@gmail.com",
    description="Utility for caching api responses from the airtable-python-wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmountjoy92/AirtableCaching",
    install_requires=["airtable-python-wrapper"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
