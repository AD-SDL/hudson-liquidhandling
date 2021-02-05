from setuptools import setup
import os


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()



setup(name='liquidhandling',
      version='0.1',
      description='A python library developed to allow programmatic control of the Hudson Robotics systems installed in Argonne National Laboratory\'s Secure BIO Lab. ',
      url='http://github.com/luckierdodge/liquidhandling',
      author='Ryan D. Lewis',
      author_email='ryan.lewis@anl.gov',
      license='MIT',
      packages=['liquidhandling'],
      keywords="robotics laboratory automation biology",
      long_description=read("README.md"),
      zip_safe=False)