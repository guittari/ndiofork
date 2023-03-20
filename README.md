# ndiofork serves as a guideline in getting a metadata query set up for RAMON

**ndio** is a Python 2 and 3 module that enables big-data neuroscience, as well as direct interfacing with NeuroData workflows and servers. More complete documentation is available at [the ndio documentation website](http://docs.neurodata.io/nddocs/ndio).

## Installation

Before you install ndio, you'll need to have a few prerequisites. The first thing to do is to **install numpy**, which often does not jive well with the auto-installation process supported by `pip`.

If you already have numpy installed, then simply run:

```
pip install ndio
```

Generally, installation failures can be fixed by running the same line again, which, yeah, that's super janky, whatever. If that still fails, try cloning the repository from https://github.com/neurodata/ndio and running `pip install -r requirements.txt`.

## Getting Started

Clone repository, ndiofork by Guittari

Save excel sheet, ramondata.xlsx in ~/ndiofork/ndio 

```
cd ndiofork
```

```brew install –cask docker’```
```cd ndio```

```Docker-compose up –d```

## Getting it to run

```poetry run flask -A main:app --debug run```

Manually start Docker containers in local application

If you are getting errors derived from bson imports (i.e., from bson import json_utils), this is probably because of a name clash between bson and pymongo 

To fix:
* ```sudo pip uninstall bson``` 
* ```sudo pip uninstall pymongo```
* ```sudo pip install pymongo```

To display json schema output, enter following URL's in Firefox:

http://localhost:5000/api/v1/ramonneuron

http://localhost:5000/api/v1/ramonsynapse

http://localhost:5000/api/v1/ramonsegment

http://localhost:5000/api/v1/ramonsubcellular

http://localhost:5000/api/v1/ramonroi










