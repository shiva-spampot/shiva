FROM ubuntu:20.04

LABEL maintainer="c0dist.g4h@gmail.com"

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y ssdeep libfuzzy-dev python3-dev libffi-dev build-essential python3.8-venv && \
  rm -rf /var/lib/apt/lists/*

# Switch to non-root user so we are not running honeypot as root
RUN useradd --create-home shiva-spampot

RUN mkdir -p /tmp/spam_queue \
  && chown -R shiva-spampot:shiva-spampot /tmp/spam_queue

WORKDIR /home/shiva-spampot
USER shiva-spampot

RUN python3 -m venv analyzer

COPY . /home/shiva-spampot/analyzer/
RUN analyzer/bin/pip install -r analyzer/requirements.txt
RUN cp analyzer/config.ini.example analyzer/config.ini

CMD ["analyzer/bin/python3", "analyzer/run_analyzer.py"]