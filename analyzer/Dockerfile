FROM ubuntu:20.04

LABEL maintainer="c0dist.g4h@gmail.com"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3.8-venv && \
    rm -rf /var/lib/apt/lists/*

# Switch to non-root user so we are not running honeypot as root
RUN useradd --create-home shiva-spampot

RUN mkdir -p /tmp/spam_queue \
  && chown -R shiva-spampot:shiva-spampot /tmp/spam_queue

WORKDIR /home/shiva-spampot
USER shiva-spampot

RUN python3 -m venv analyzer

COPY src/ /home/shiva-spampot/analyzer/
RUN analyzer/bin/pip install -r analyzer/requirements.txt

CMD ["analyzer/bin/python3", "analyzer/run_analyzer.py"]