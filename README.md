# HTW_V2H_SS25
This project demonstrates how to create a bev time series with Emobpy and integrate it into an energy system in Oemof.

## Citation

This project makes use of [emobpy](https://gitlab.com/diw-evu/emobpy/emobpy)
and [Oemof-solph](https://github.com/oemof/oemof-solph)
If you use this project in scientific work, please cite this repo and these two Libs as well.


## Features
- Generation of mobility, consumption, and load time series  
- Integration with energy system models using Oemof  
- Reproducible pipelines (conda environments)  

## Installation - Emobpy
```bash
conda env create -f environment_emobpy.yml
conda activate emobpy_py36
## Installation - Oemof
```bash
conda env create -f environment_oemof.yml
conda activate oemof_solve_py312

