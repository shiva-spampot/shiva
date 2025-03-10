# SHIVA Spampot

**Disclaimer:**  
This project is currently under development and is not recommended for production use. It may contain bugs, unfinished features, and breaking changes. Use it at your own risk.

**NOTE**: This project's original source has been moved to
[shiva-legacy](https://github.com/shiva-spampot/shiva-legacy).

- [Background](#background)
- [Components](#components)
  - [Receiver](#receiver)
  - [Analyzer](#analyzer)
- [Database Schema](#database-schema)
- [Running](#running)
  - [Receiver](#receiver-1)
  - [Analyzer](#analyzer-1)
- [To Do](#to-do)

## Background

SHIVA: Spam Honeypot with Intelligent Virtual Analyzer, is a Spam Honeypot (SpamPot). SHIVA acts as an SMTP server which can be configured to act as an open-relay or authenticated mail server. SHIVA is written in Python 3 and extends `aiosmtpd` for implementing SMTP capabilities. For the database, SHIVA uses PostgreSQL for storing information parsed from the received spams. Analysis of data captured can be used to get information of phishing attacks, scamming campaigns, malware campaigns, spam botnets, etc.

Originally, SHIVA was initially developed around 2012 under The Honeynet Project. SHIVA was also a part of the Google Summer of Code program in 2013. It used the Lamson library and monkey-patched the library with a lot of custom code. However, due to difficulty to maintain the code and lack of time, the project was not updated regularly. The old code was very hard to maintain/customize and hence a decision was taken to rewrite it from scratch. Current efforts focus on simplifying the codebase, and adding features like easy deployment via Docker, better documentation, PostgreSQL integration for search/analysis, threat intel service lookups, updated OSS licence, etc.

---

## Components

The spampot is divided into two components: Receiver and Analyzer. The decision was taken to ensure that both the components keep working regardless of load on the other part. Receiving and dumping emails is relatively a simpler task than parsing emails. Therefore, both the components can run simply in their own Docker containers, collaborating using a single shared directory.

### Receiver

Receiver essentially is an SMTP server which accepts all emails thrown at it. These spam emails are then validated against various checks. Once validates, we extract the basic metadata from them and then the email is dumped as a file in the shared email queue directory. As of now, we only support a directory for sharing the emails between the Receiver and Analyzer. However, in future, we can add more storage providers based on the use case and requirements. The receiver also support authentication and custom credentials can be provided to add authenticity.


### Analyzer

Analyzer is the actual brain of the operation and responsible for parsing and analysing spams. This component keeps a watch on the shared email queue directory and as soon as a new spam is received, it parses the email file, extracts all the important fields and then checks if we have seen this spam already. To avoid saving duplicate messages, Analyzer calculates SHA-1 and SSDEEP hash for each email and discards the exact same emails. For emails that might be almost similar, we also compare the SSDEEP hash with existing ones (however it is not much useful for emails under 4 KB) and discard if the similarity is above a certain threshold. Depending on the result, the email is either added to an existing campaign or a new campaign is created. All the collected data is then stored in the PostgreSQL database.


As mentioned above, both the components are independent and can be run via terminal or Docker. The components don’t need to be on the same box as long as they can access a shared folder.

---

## Database Schema

Here is the visual representation of the database schema:
You can view the database schema by clicking the link below:

[View Database Schema](images/Shiva-Schema.png)

---

## Running all Components

Run below command to start Reciever, Analyzer and PostgreSQL

```shell
docker compose up
```

## Running Individually

### Receiver

The easiest way to run Receiver is via Docker. To build the Receiver, clone this project and run in source directory:

```bash
cd receiver/
docker build -t shiva-spampot/receiver .
```

Once the command completes, you can following command to start the container:

```bash
docker run --name=shiva-receiver -d -h smtp.somedomain.com \
       -p "0.0.0.0:2525:2525" -v spam_queue:/tmp/spam_queue/ shiva-spampot/receiver
```

To change the container's host name, replace the value passed to `-h` switch in above command. By default the container will also start listening for spams on port 2525. The container will also dump all the emails in a Docker volume - `spam_queue`. You can also pass following environment variables:

- SHIVA_HOST: Defaults to 0.0.0.0, i.e. listen on all interfaces.
- SHIVA_PORT: Defaults to port 2525.
- QUEUE_DIR: Directory to dump all spams in.
- THRESHOLD: SSDEEP similarity ratio, defaults to 94.
- SENSOR_NAME: Name of honeypot instance, defaults to hostname of container.

### Analyzer

The easiest way to run Analyzer is via Docker. To build the Analyzer, clone this project and run in source directory:

```bash
cd analyzer/
docker build -t shiva-spampot/analyzer .
```

Once the command completes, you can following command to start the container:

```bash
docker run -it --name=shiva-analyzer -d -v spam_queue:/tmp/spam_queue/ shiva-spampot/analyzer
```

---

## To Do

- [x] Add support for SMTP authentication
- [x] Add Analyzer code
- [x] Email parsing (basic)
- [ ] Virustotal lookup for attachments
- [x] Extract URLs from mail body
- [x] Index records in PostgreSQL
