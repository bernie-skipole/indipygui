# indipygui
GUI client to connect to an INDI service

**Currently being built, not yet ready for use, not yet available on PyPI.**

indipygui uses the tkinter package, which some Python distributions do not include, as it is a system package it cannot be installed from PyPI. If using debian, or debian derived distributions you may need to install tkinter with:

sudo apt install python3-tk

Currently indipygui is not on PyPI, but can be installed from github. It may only have partial functionality.

Create and activate a virtual environment, and then install with:

pip install git+https://github.com/bernie-skipole/indipygui

This also installs several further dependencies from pypi.

Then run the program with:

python -m indipygui

The package help is:

    usage: indipygui [options]

    Client to communicate to an INDI service.

    options:
      -h, --help               show this help message and exit
      --port PORT              Port of the INDI server (default 7624).
      --host HOST              Hostname/IP of the INDI server (default localhost).
      --blobfolder BLOBFOLDER  Optional folder where BLOB's will be saved.

      --version    show program's version number and exit



This client should work with any INDI service, however associated packages by the same author are:

## indipyserver

A Python INDI server, serves INDI drivers on a port.

https://github.com/bernie-skipole/indipyserver

https://pypi.org/project/indipyserver/

https://indipyserver.readthedocs.io

## indipydriver

Package with classes used to create INDI drivers.

https://github.com/bernie-skipole/indipydriver

https://pypi.org/project/indipydriver

https://indipydriver.readthedocs.io

## indipyweb

Web server and INDI client, connects to an INDI serving port, and serves client pages for connected browsers.

https://github.com/bernie-skipole/indipyweb

https://pypi.org/project/indipyweb

## indipyterm

A terminal based INDI client, connects to an INDI serving port.

https://github.com/bernie-skipole/indipyterm

https://pypi.org/project/indipyterm/

