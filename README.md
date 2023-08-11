# GSP-python [![](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## A Python implementation of the Generalized Sequential Patterns (GSP) algorithm for sequential pattern mining

This project implements the Generalized Sequential Patterns (GSP) algorithm to find frequent sequences within a given
dataset. This implementation includes parameters for the _mingap_, _maxgap_, and _maxspan_ time constraints.

The project also features a simple dataset generator.

---

## Installation

The package can be installed via pip:

```
python3 -m pip install gsp_python
```

---

## Usage

The GSP algorithm and the dataset generator can be executed either from the command line or by importing the package modules in a script.

---

### From the command line

To run the GSP algorithm:

```
python3 -m gsp_python GSP infile outfile minsup -t maxgap mingap maxspan
```
Where:

- `infile`: specifies the path of the file containing the dataset from which sequences must be mined from. The file must be a text file in which each data-sequence is terminated by ' -2', each element is terminated by ' -1', and each event is separated by a space.
- `outfile`: specifies the path of the output file where the result will be printed to. It will contain all frequent sequences found, each paired with their support count.
- `minsup`: specifies the minimum support threshold used during execution.
- `-t maxgap mingap maxspan` (optional): specifies the _maxgap_, _mingap_, and _maxspan_ values used during execution. If not specified, the default values of _inf_, 0, and _inf_ will be used instead.

For more information about additional optional arguments, type:

```
python3 -m gsp_python GSP -h
```

---

To generate a random dataset:

```
python3 -m gsp_python DatasetGen outfile size nevents maxevents avgelems
```
Where:

- `outfile`: specifies the path of the output file where the dataset will be printed to. The format used is the same as the one accepted as input for the algorithm above.
- `size`: specifies the number of data-sequences.
- `nevents`: specifies the number of unique events.
- `maxevents`: specifies the maximum number of events per element.
- `avgelems`: specifies the average number of elements per data-sequence.

For more information about additional optional arguments, type:

```
python3 -m gsp_python DatasetGen -h
```

---

### From within a script

To run the GSP algorithm, use `gsp_python.gsp.GSP()` to create and initialize a `GSP` object, providing the required arguments; then, call method `run_gsp()` to execute the algorithm (the result is returned as a list of tuples, each pairing a sequence with its support count).

An example is given below:

```python
from gsp_python.gsp import load_ds
from gsp_python.gsp import GSP

dataset, dict1, dict2 = load_ds("path/to/file.txt")

algo_gsp = GSP(dataset, minsup=0.3, mingap=1, maxgap=2, maxspan=5)
output = algo_gsp.run_gsp()
```

Method `load_ds()` loads the dataset contained in the file at the specified path (provided that it follows the format explained above), converting all events to integers. It also returns the dictionary (here assigned to `dict1`) that can be used to convert each integer back to the corresponding event.

---

To generate a random dataset, use `gsp_python.dataset_gen.DatasetGenerator()` to create and initialize a `DatasetGenerator()` object, providing the required arguments; then, call method `generate_sequence_dataset()` to generate a dataset (the dataset is returned as a `list[list[list[int]]]`).

An example is given below:

```python
from gsp_python.dataset_gen import DatasetGenerator

algo_dsgen = DatasetGenerator(size=100, nevents=8, maxevents=4, avgelems=16)
algo_dsgen.generate_sequence_dataset()
```