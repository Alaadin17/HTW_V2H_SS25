# HTW_V2H_SS25
This project demonstrates how to create a bev time series with Emobpy and integrate it into an energy system in Oemof.

## Citation

This project makes use of [emobpy](https://gitlab.com/diw-evu/emobpy/emobpy)
and [Oemof-solph](https://github.com/oemof/oemof-solph)
If you use this project in scientific work, please cite these two Libs as well.


## Features
- Generation of mobility, consumption, and load time series  
- Integration with energy system models using Oemof  
- Configuration via YAML/CSV files  
- Reproducible pipelines (virtual environments + requirements files)  

## Installation
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
