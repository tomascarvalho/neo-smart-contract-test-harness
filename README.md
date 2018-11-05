# NEO Smart Contract Test Harness
A testing harness allowing a user to create unit tests for NEO smart contracts

## Requires

* Pipenv
* Redis
* Python3

## Running Instructions

* Make sure you have python3 installed
* Create a virtual environment `python -m venv venv`
* Activate the virtual environment `source venv/bin/activate`
* Install requirements `pip install -r requirements.txt`
* Run redis `redis-server`
* cd to tasks folder `cd tasks`
* Run celery `celery -A tasks worker -l info`
* Run the node listener `python runnode.py`
