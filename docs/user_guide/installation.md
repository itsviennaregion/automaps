!!! warning

    Only tested on Ubuntu 20.04! Installation on Windows is experimental.

## Requirements

autoMaps requires a recent version of [Python](https://www.python.org/), the Python 
package manager, [pip](https://pip.pypa.io/en/stable/installation/), and the free and
open source geographic information system [QGIS](https://qgis.org/) to be installed on
your system.

You can check if you already have these installed from the command line:

    $ python --version
    Python 3.8.2
    $ pip --version
    pip 20.0.2 from /usr/local/lib/python3.8/site-packages/pip (python 3.8)
    $ qgis --version
    QGIS 3.18.1-Zürich 'Zürich' (202f1bf7e5)

If you already have those packages installed, you may skip down to [Installing
autoMaps](#installing-automaps).

### Installing Python

Install [Python](https://www.python.org/) using your package manager of choice, or by 
downloading an installer appropriate for your system from 
[python.org](https://www.python.org/downloads) and running it.

### Installing pip

If you're using a recent version of Python, the Python package manager, 
[pip](https://pip.pypa.io/en/stable/installation/), is most likely installed by default.
However, you may need to upgrade pip to the lasted version:

    pip install --upgrade pip

If you need to install pip for the first time, download 
[get-pip.py](https://bootstrap.pypa.io/get-pip.py). Then run the following command to
install it:

    python get-pip.py

### Installing QGIS

autoMaps uses [QGIS](https://qgis.org/), a free and open source geographic information
system, to generate maps. Get it on the 
[QGIS downloads page](https://qgis.org/en/site/forusers/download.html) and install it
first. You probably should be familiar with QGIS and at least a little bit of `PyQGIS`
to get most out of autoMaps. Check out the
[QGIS documentation](https://qgis.org/en/docs/index.html), if necessary.

## Installing autoMaps

Install the `automaps` package from [PyPI](https://pypi.org/project/automaps/)
__for the Python interpreter used by QGIS__, for example like this:

    /usr/bin/python3 -m pip install automaps

!!! info

    If you are not sure, which Python interpreter is used by QGIS, open the QGIS GUI and
    run the following commands in the Python console: 
        
        import sys
        sys.executable

    This may return something like `/usr/bin/python3`. Use the path to this Python
    interpreter in the command above.

!!! info

    You may also install the `automaps` package into a Python virtual environment. This
    keeps your system Python nice and clean. As `qgis` cannot be installed via pip,
    you have to take an extra step to access this package from within the virtual
    environment: To tell the Python interpreter of your virtual environment, where the
    `qgis` package is located, you have to add a `.pth` file (e.g., `qgis.pth`) to its
    `.../site-packages/` directory (see
    [Python docs](https://docs.python.org/3/install/index.html#modifying-python-s-search-path)).

    You can find out, which path you have to write into the file, by running:

        <PATH_TO_YOUR_SYSTEM_PYTHON_INTERPRETER> -c "import qgis; print(qgis.__path__[0])"

    e.g.

        /usr/bin/python3 -c "import qgis; print(qgis.__path__[0])"

    Assuming 
    
    * this results in the path `/usr/lib/python3/dist-packages/qgis`, 
    * that your system Python interpreter is located under `/usr/bin/python3`,
    * and that you are using Python version 3.8, 
    
    the procedure to install automaps into a new virtual environment is as follows:

    Create the virtual environment:

        /usr/bin/python3 -m venv venv
    
    Activate the virtual environment:

        source venv/bin/activate

    Install autoMaps:

        pip install automaps

    Create the `.pth` file:

        echo "/usr/lib/python3/dist-packages" > venv/lib/python3.8/site-packages/qgis.pth

!!! info

    If you are trying to install `autoMaps` on Windows, the method to find the Python
    interpreter described above may not work, as it yields only the path to the
    `qgis.exe` as a result. Try to locate a file called `python-qgis.bat` in the same
    directory as `qgis.exe` and use it to start the correct Python interpreter.
