# SHIVA Spampot

**NOTE**: This project's original source has been moved to 
[shiva-legacy](https://github.com/shiva-spampot/shiva-legacy).

## Background

SHIVA: Spam Honeypot with Intelligent Virtual Analyzer, is an open but controlled relay Spam Honeypot (SpamPot). SHIVA is written in Python 3 and will eventually use Elasticsearch for storing information parsed from the received spams. Analysis of data captured can be used to get information of phishing attacks, scamming campaigns, malware campaigns, spam botnets, etc.

Originally, SHIVA was initially developed during 2012/2013 and used the Lamson framework in the background. However, due to lack of time, the project was not updated regularly. The old code was complicated and had a lot of monkey-patching which made it harder to maintain. Current efforts will focus on simplifying the codebase, and adding features like easy deployment via Docker, better documentation, Elasticsearch integration for search/analysis, threat intel service lookups, updated OSS licence, etc.



## Components

The spampot is divided into two components: Receiver and Analyzer. The decision was taken to ensure that both the components keep working regardless of load on the other part. Receiving and dumping emails is relatively a simpler task than parsing emails. Therefore, both the components can run simply in their own Docker containers, collaborating using a single shared directory.

Receiver essentially is an SMTP server which accepts all emails thrown at it. The email along with the metadata like sender IP, email, recipients, SSDEEP hash, etc is dumped in a directory. This directory is also monitored by Analyzer to parse these emails. To avoid saving duplicate messages, Receiver calculates SHA-1 and SSDEEP hash for each email and discards the exact same emails. For emails that might be almost similar, we also compare the SSDEEP hash with existing ones (only if the email size is over 4KB) and discard if the similarity is above a certain threshold. We aim to add support for authentication and SSL communication in future versions.

Analyzer (still in development) is the actual brain of the operation and responsible for parsing and analysing spams.The analyzer picks spams from directory shared with receiver and parses the .eml and metadata file. It extracts information such as recipients, URLs, attachments, mail body, etc. Indicators extracted from the email can then be queries via 3rd party integrations such as Virustotal, Hatching Triage, etc., if these are configured with API keys. This extracted information is then indexed in Elasticsearch for easier searching and analysis later. This information can also be shared with other analysts/researchers via Hpfeeds integration.

As mentioned above, both the components are independent and can be run via terminal or Docker. The components don’t need to be on the same box as long as they can access a shared folder.


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

The easiest way to run Analyzer is via Docker. To build the Analyzer, clone this project and run in source directory:

```bash
docker build -t shiva-spampot/analyzer -f Dockerfile_analyzer  .
```
Once the command completes, you can following command to start the container:

```bash
docker run -it --name=shiva-analyzer -d -v spam_queue:/tmp/spam_queue/ shiva-spampot/analyzer
```
Right now, the logic to parse emails is still in development and analyzer code is being added regularly.

## To Do

- [ ] Add support for SMTP authentication
- [x] Add Analyzer
- [ ] Finish Analyzer
