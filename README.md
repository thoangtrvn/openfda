## Package preparation

Having [anaconda or miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html) is recommended. 

The information to setup the environment using conda is thus provided.
Assuming the machine is running Mac O/S, the environment file **py37_macosx.txt** contains the list of packages
Runt the following commands to help building conda 'py37' environment

```console
conda create --name py37 --file py37_macosx.txt

source activate py37
```

To be able to use python from this environment as the backend inside jupyter lab, we run
```console
python -m ipykernel install --user --name py37 --display-name "Python (py37)"
```

To enrich jupyter lab, you can add the some additional widgets
```console
chmod +x ./extensions_jupyterlab.sh
./extensions_jupyterlab.sh
```

Finally, at the same location of this file, run this command from the terminal
```console 
jupyter lab
```
and select 'Python (py37)' as the backend.# openfda


Register an email with OpenFDA, and put the key into the new file (to have more requests/minute)
```console
openfda_key.txt
```

The work is organized into 2 files:

1. stage_1: effort to understand data

2. stage_2: effort to analyze data

The pre-generated outputs are saved into HTML file, and can be viewed using 
[Github HTML preview](https://htmlpreview.github.io/?)
