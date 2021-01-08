# liquidhandling

This repository contains the source code for a python library developed to allow programmatic control of the Hudson Robotics systems installed in Argonne National Laboratory's Secure BIO Lab.

## Installing and using this Repository (Currently in development)

1. Install [Python 3.8+](https://www.python.org/downloads/), making sure to include pip in the install
1. Git clone this repository: `git clone https://xgitlab.cels.anl.gov/rarvind/liquidhandling.git`
1. Run `pip install -r requirements.txt` in the repository root
1. Use python to run the `example/solo_soft_example.py` and open the `example.hso` file it generates in SoloSoft to test your setup.


## Tests

* Run all: `python -m pytest test` in the repo's root directory

## Formatting the Code

To automatically format the code for style and readability, run `black .` in the repo's root directory. This keeps all of our python code stylistically consistent.

## Development

## Recommended Visual Studio Code Extensions

* Better Comments by Aaron Bond
* GitLens by Eric Amodio
* Pylance by Microsoft
* Python by Microsoft
* Visual Studio IntelliCode by Microsoft