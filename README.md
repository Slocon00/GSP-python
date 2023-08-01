# GSP-python [![](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## A Python implementation of Generalized Sequential Patterns (GSP) algorithm for sequential pattern mining

This project implements the Generalized Sequential Patterns (GSP) algorithm to find frequent sequences within a given
dataset. This implementation includes parameters for the _mingap_, _maxgap_, and _maxspan_ time constraints.

The project also features a simple dataset generator.

### Installation

```
python3 -m pip install gsp_py
```

### Usage

To run the gsp algorithm:

```
python3 -m gsp-python GSP infile outfile minsup -t maxgap mingap maxspan
```

To generate a random dataset:

```
python3 -m gsp-python DatasetGen outfile size nevents maxevents avgelems
```

---

For more information about arguments and additional optional arguments, type:

```
python3 -m gsp-python GSP -h
```

or

```
python3 -m gsp-python DatasetGen -h
```

---

Alternatively, the modules can be manually imported and used in a script.
An example is given below:

```
from gsp_py.gsp import load_ds
from gsp_py.gsp import GSP

dataset, {}, {} = load_ds("path/to/file.txt")

algo_gsp = GSP(dataset, minsup=0.3, mingap=1, maxgap=2, maxspan=5)
output = algo_gsp.run_gsp()
```