# README

Welcome to the MEFL repository! Thank you for your support of this project!! This repository contains the implementation source code of MEFL, as well as experimental result data for MEFL and baselines (including their various variants).

## Runtime Environment
MEFL's main working environment:
- `python3: 3.10.12`
- `gcov: 13.1.0`
- `gcc: 13.1.0`
- `c++: 13.1.0`
- `Ubuntu: 22.04.3`
- `CPU: Intel Xeon CPU E5-2680 v4@2.40GHz with 251G memory`
- `llvm-IRMutator source code version: 15.0.4`

## Introduction to MEFL's Main Files
- `my-src`: MEFL source code directory
  - `my-src/config`: Path configuration directory
    - `config.ini`: Contains path information for multiple working files/directories. Note that `mefl_path` doesn't need manual configuration. `setup.py` will use `os.getcwd` to get the current directory and modify `mefl_path` during runtime.
  - `auto-exps.py`: Performs bug isolation for multiple data points
  - `main.py`: Called by `auto-exps.py` to execute bug isolation for a single data point
  - `utils.py`: Defines various utility functions
  - `setup.py`: Performs necessary configuration work before isolation, such as modifying paths in `config.ini`
  - `eval.py`: Analyzes coverage information of all data points in `exp-results` (this directory will be generated after `setup.py`) to obtain `Top-n/MAR/MFR` metric values
- `llvm-15-bin`: Contains necessary binary executables for MEFL's operation, such as `llvm-my-fuzzer` (the mutator implemented using LLVM's three mutation operators).
- `experiment-ready`: Dataset directory
  - `experiment-ready/llvmbugs`
    - `1.fail`: Input IR file (binary format)
    - `fail.c`: Input C file (`baseline` techniques require `C-level` input)
    - `locations`: Various information about this bug
  - `experiment-ready/llvm-versions`: Directory for different version compilers, initially empty. `auto-exps.py` contains code for building `llvm`.
- `experiment_results`: Contains isolation result files for each data point from `MEFL, ETEM, ODFL, RecBi` and related method variants

## How to run MEFL
```shell
# step 1: clone the project
git clone git@github.com:watermelonAnonymous/ASE25.git
# step 2: Enter working directory
cd ./ASE25/MEFL
# step 3: Perform necessary configurations
python3 setup.py
# step 4: Run bug isolation program
python3 auto-exps.py
# step 5: Obtain evaluation results for metrics
python3 eval.py
```

Friendly reminder:
- Running one data point takes approximately 1 hour (excluding time to build the faulty LLVM version)
- `auto-exps.py` contains logic for building compilers corresponding to each data point's faulty LLVM version. Since coverage information needs to be collected, the build process involves instrumentation and requires significant space (about 50G per build, totaling approximately 4.6T - please reserve sufficient space). Additionally, building also takes considerable time (in the author's experimental environment, building with make -j64 takes about 15 minutes per build).
