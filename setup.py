"""Script to deploy the package"""

from setuptools import setup, find_packages
from deploy import Deploy

deploy = Deploy()

setup(
    name=deploy.project_name,
    version=deploy.package_version,
    author=deploy.author,
    author_email=deploy.author_email,
    description=deploy.description,
    long_description=deploy.long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=deploy.requirements,
    license='Apache License 2.0',
    url=deploy.url,
    # Classifiers can be found at: https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
