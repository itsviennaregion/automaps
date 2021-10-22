!!! warning

    Only tested on Ubuntu 20.04!

# Requirements
autoMaps requires a recent version of [Python](https://www.python.org/), the Python 
package manager, [pip](https://pip.pypa.io/en/stable/installation/), and the free and
open source geographic information system [QGIS](https://qgis.org/) to be installed on
your system.

You can check if you already have these installed from the command line:

```bash
$ python --version
Python 3.8.2
$ pip --version
pip 20.0.2 from /usr/local/lib/python3.8/site-packages/pip (python 3.8)
$ qgis --version
QGIS 3.18.1-Zürich 'Zürich' (202f1bf7e5)
```

If you already have those packages installed, you may skip down to [Installing
autoMaps](#installing-automaps).


## Installing Python
Install [Python](https://www.python.org/) using your package manager of choice, or by 
downloading an installer appropriate for your system from 
[python.org](https://www.python.org/downloads) and running it.


## Installing pip
If you're using a recent version of Python, the Python package manager, 
[pip](https://pip.pypa.io/en/stable/installation/), is most likely installed by default.
However, you may need to upgrade pip to the lasted version:

```bash
pip install --upgrade pip
```

If you need to install pip for the first time, download 
[get-pip.py](https://bootstrap.pypa.io/get-pip.py). Then run the following command to
install it:

```bash
python get-pip.py
```


## Installing QGIS
autoMaps uses [QGIS](https://qgis.org/), a free and open source geographic information
system, to generate maps. Get it on the 
[QGIS downloads page](https://qgis.org/en/site/forusers/download.html) and install it
first. You probably should be familiar with QGIS and at least a little bit of `PyQGIS`
to get most out of autoMaps. Check out the
[QGIS documentation](https://qgis.org/en/docs/index.html), if necessary.


# Installing autoMaps
Open your command line and clone the autoMaps repository:
```bash
git clone https://gitlab.com/its-vienna-region/digilab/automatisierte-karten
```

Change into the cloned directory:
```bash
cd automatisierte-karten
```

Install the `automaps` package __for the Python interpreter used by QGIS__, for 
example like this:
```bash
/usr/bin/python3 -m pip install .
```

!!! info

    If you are not sure, which Python interpreter is used by QGIS, open the QGIS GUI and
    run the following commands in the Python console: 
        
        import sys
        sys.executable

    This may return something like `/usr/bin/python3`. Use the path to this Python
    interpreter in the command above.

