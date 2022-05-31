# SHIVA Spampot

**NOTE**: This project's original source has been moved to 
[shiva-legacy](https://github.com/shiva-spampot/shiva-legacy).

## Background

SHIVA: Spam Honeypot with Intelligent Virtual Analyzer, is an open but controlled relay Spam Honeypot (SpamPot). SHIVA is written in Python 3 and will eventually use Elasticsearch for storing information parsed from the received spams. Analysis of data captured can be used to get information of phishing attacks, scamming campaigns, malware campaigns, spam botnets, etc.

Originally, SHIVA was initially developed during 2012/2013 and used the Lamson framework in the background. However, due to lack of time, the project was not updated regularly. The old code was complicated and had a lot of monkey-patching which made it harder to maintain. Current efforts will focus on simplifying the codebase, and adding features like easy deployment via Docker, better documentation, Elasticsearch integration for search/analysis, threat intel service lookups, updated OSS licence, etc.



## Components

The spampot is divided into two components: Receiver and Analyzer. Receiver essentially is an SMTP server which accepts all emails thrown at it. The email along with the metadata like sender IP, email, recipients, SSDEEP hash, etc is saved in a directory. This directory is also monitored by Analyzer to parse these emails. To avoid saving duplicate messages, Receiver calculates SHA-1 hash for each email and discards the exact same emails. For emails that are almost similar, we also calculate SSDEEP hash, compare with existing ones (if the email size is over 4KB) and discard if the similarity is above a certain threshold.

Analyzer is still in development.

## Running Receiver

The easiest way to run Receiver is via Docker. To build the Receiver, clone this project and run in source directory:

```bash
docker build -t shiva-spampot/receiver -f Dockerfile_receiver  .
```
Once the command completes, you can following command to start the container:

```bash
docker run --name=shiva-receiver -d -h smtp.somedomain.com \
       -p "0.0.0.0:2525:2525" -v spam_queue:/tmp/spam_queue/ shiva-spampot/receiver
```

To change the container's host name, replace the value passed to `-h` switch in above command. By default the container will also start listening for spams on port 2525. The container will also dump all the emails in a Docker volume - `spam_queue`. You can also pass following environment variables:
* SHIVA_HOST: Defaults to 0.0.0.0, i.e. listen on all interfaces.
* SHIVA_PORT: Defaults to port 2525.
* QUEUE_DIR: Directory to dump all spams in.
* THRESHOLD: SSDEEP similarity ratio, defaults to 94.
* SENSOR_NAME: Name of honeypot instance, defaults to hostname of container.

## Running Analyzer

TBD

## To Do

- [ ] Add support for SMTP authentication
- [ ] Add Analyzer
