# ndiofork 

This repository is a forked version of **ndio** that serves as a guideline in getting a metadata query set up for RAMON created by Nicole Guittari

**ndio** is a Python 2 and 3 module that enables big-data neuroscience, as well as direct interfacing with NeuroData workflows and servers. More complete documentation is available at [the ndio documentation website](http://docs.neurodata.io/nddocs/ndio).

## Installation

The first thing to do is to **install numpy**, which often does not jive well with the auto-installation process supported by `pip`.

If you already have numpy installed, then simply run:

```
pip install ndio
```

Generally, installation failures can be fixed by running the same line again. If that still fails, try cloning the repository from https://github.com/neurodata/ndio and running `pip install -r requirements.txt`.

## Getting Started

Clone repository, ndiofork by Guittari

Save excel sheet, ramondata.xlsx in ~/ndiofork/ndio 

```
cd ndiofork
```

```
brew install –cask docker
```

```
cd ndio
```

```
Docker-compose up –d
```

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

## Ouptut

<img width="508" alt="image" src="https://user-images.githubusercontent.com/66258538/226371140-0d8b283b-18fe-4664-b961-aa1caef7db41.png">

<img width="468" alt="image" src="https://user-images.githubusercontent.com/66258538/226371188-4dc86cab-5829-47a5-a52c-0f24653ca1e9.png">

<img width="442" alt="image" src="https://user-images.githubusercontent.com/66258538/226371377-9ec40332-21a2-44d9-8714-c9411ef82fca.png">

<img width="424" alt="image" src="https://user-images.githubusercontent.com/66258538/226371418-ad4e7edd-c689-4f13-bd1e-420a7480c311.png">

<img width="358" alt="image" src="https://user-images.githubusercontent.com/66258538/226371454-edba1eb7-f6ee-4c3f-89f4-54a36d9f86cf.png">



## Next Steps 

Shifting away from manually entering in the CSV, ramondata.xlsx is an important goal to avoid manual errors, maintain consistency, and promote collaboration between members of the connectomic community. 

Current efforts involve editing, /mossmetadataintegration/neurodata for the computational gathering of neuronal entities. 









