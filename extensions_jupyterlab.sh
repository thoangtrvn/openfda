set NODE_OPTIONS=--max-old-space-size=4096
jupyter labextension install         @jupyter-widgets/jupyterlab-manager@1.1.0 --no-build
jupyter labextension install         @jupyterlab/git@0.9.0 --no-build
jupyter labextension install         @jupyterlab/github@1.0.1 --no-build
jupyter labextension install         @jupyterlab/google-drive@1.0.0 --no-build
jupyter labextension install         jupyterlab_vim@0.11.0 --no-build
jupyter labextension install         nbdime-jupyterlab@1.0.0 --no-build
jupyter lab build
set NODE_OPTIONS=
