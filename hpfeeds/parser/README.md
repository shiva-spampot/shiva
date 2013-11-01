What's this?
------------
This parser can be used to receive data sent by SHIVA on `shiva.parsed` channel and store it in local database after parsing it. The module is only for parsing the data received from `shiva.parsed` channel. 
The parser can be used without setting up the rest of SHIVA. It has been provided as an add-on feature.
Module is divided into 2 main scripts:

* subscribe.py: This script subscribes to the `shiva.parsed` channel and receives the data. After receiving a record, it simply dumps it in a local file, for further processing.
* corelate.py: This script picks up the record dumped by subscribe.py and converts it to a dictionary for processing. After analyzing the data, it is saved in the database.

Prerequisites
--------------
Following dependencies must be installed in system
* mysql-client
* cython
* ssdeep
* MySQL-python

These dependencies can be installed as

```shell
$ sudo apt-get install mysql-client
$ sudo pip install cython
$ sudo pip install ssdeep
$ sudo pip install MySQL-python
```

Setting Up
----------
* Edit `dbcreate.py` and provide the necessary database parameters.
* Edit `corelate.py` and provide the necessary database parameters.
* Make two folders where you want to run this, namely `spams` and `attach`
* Create database by executing dbcreate.py as `python dbcreate.py`
* Edit `subscribe.py` and provide necessary Hpfeeds parameters.

Running
-------
* Open up two terminal tabs/ windows.
* Run `subscribe.py` in one terminal as `python subscribe.py`.
* Run `corelate.py` in another terminal as `python corelate.py`.

Author
-------
* Rahul Binjve