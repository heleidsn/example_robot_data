# Example robot URDFs

[![pipeline status](https://gitlab.laas.fr/gepetto/example-robot-data/badges/master/pipeline.svg)](https://gitlab.laas.fr/gepetto/example-robot-data/-/commits/master)
[![conde version](https://img.shields.io/conda/vn/conda-forge/example-robot-data.svg)](https://anaconda.org/conda-forge/example-robot-data)
[![conde download](https://anaconda.org/conda-forge/example-robot-data/badges/downloads.svg)](https://anaconda.org/conda-forge/example-robot-data)
[![PyPI version](https://badge.fury.io/py/example-robot-data.svg)](https://badge.fury.io/py/example-robot-data)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/gepetto/example-robot-data/master.svg)](https://results.pre-commit.ci/latest/github/gepetto/example-robot-data/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository is forked from PepMS's [repo](https://github.com/PepMS/example-robot-data) used for eagle mpc project.

## What's new

- Added s500_quadrotor and s500_uam for personal project.

## Installation

### :turtle: With ROS

Just clone it (with `--recursive`) into a catkin workspace.

### :file_folder: From source

Clone it (with `--recursive`), create a `build` directory inside, and:

```bash
cmake .. && make && make install
```

## :robot: Show a robot with [gepetto-gui](https://github.com/gepetto/gepetto-viewer-corba)

`python -m example_robot_data -h` to list available robots.

## :copyright: Credits

### :writing_hand: Written by

- [Carlos Mastalli](https://cmastalli.github.io/), Heriot-Watt University :uk:
- [Guilhem Saurel](https://github.com/nim65s), LAAS-CNRS :fr:

### :construction_worker: With contributions from

- [Justin Carpentier](https://jcarpent.github.io/), INRIA :fr:
- [Pierre Fernbach](https://pfernbach.github.io/), LAAS-CNRS :fr:
- [Florent Lamiraux](https://gepettoweb.laas.fr/index.php/Members/FlorentLamiraux), LAAS-CNRS :fr:
- [Wolfgang Merkt](http://www.wolfgangmerkt.com/research/), University of Oxford :uk:
- [Josep Martí Saumell](https://www.iri.upc.edu/staff/jmarti), IRI: CSIC-UPC :es:
- [Louis Montaut](https://lmontaut.github.io/), INRIA :fr:, CTU :czech_republic:
- [Sergi Martinez](https://www.romilab.org/team/sergi-martinez), Heriot-Watt University :uk:
