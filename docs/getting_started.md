# Getting Started with autoMaps

## Installation
__Only tested on Ubuntu 20.04!__

autoMaps uses QGIS to generate maps. Get it on the 
[QGIS downloads page](https://qgis.org/en/site/forusers/download.html) and install it
first.

Then open your command line and clone the autoMaps repository:
```bash
git clone https://gitlab.com/its-vienna-region/digilab/automatisierte-karten
```

Change into the cloned directory:
```bash
cd automatisierte-karten
```

Install the `automaps` package (__for the Python interpreter used by QGIS!__): 
```bash
python3 -m pip install .
```

## Creating a demo project
Do get a feeling for the functionality and configuration of autoMaps you should first
create a demo project.

On the command line, `cd` into a directory where you want to place the demo project.
Then run the following command:
```bash
automaps init-demo
``` 

Then start the demo app by running the following command:
```bash
automaps run ./automaps-demo/app.py
``` 

Open up `http://http://127.0.0.1:8506/automaps-demo/` in your browser, and you'll see
the frontend of the demo project being displayed:
![Demo Frontend](img/demo_frontend.png)

Choose a district and a file format, click on `Create map` and then on `Download` to get
your first automatically generated map.