from setuptools import setup, find_packages
import os



with open('README.rst') as f:
    long_description = f.read()

install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)

setup(
    name="liquidhandling",
    version="0.1.39",
    description="A python library developed to allow programmatic control of the Hudson Robotics systems installed in Argonne National Laboratory's Secure BIO Lab. ",
    url="http://github.com/luckierdodge/liquidhandling",
    author="Ryan D. Lewis",
    author_email="ryan.lewis@anl.gov",
    license="MIT",
    keywords="robotics laboratory automation biology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["liquidhandling"],
    install_requires=install_requires,
    
)
