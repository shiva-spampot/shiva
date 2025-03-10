FROM ubuntu:20.04

LABEL maintainer="c0dist.g4h@gmail.com"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3-dev libffi-dev build-essential python3.8-venv && \
    rm -rf /var/lib/apt/lists/*

# Switch to non-root user so we are not running honeypot as root
RUN useradd --create-home shiva-spampot

RUN mkdir -p /tmp/spam_queue \
    && chown -R shiva-spampot:shiva-spampot /tmp/spam_queue

WORKDIR /home/shiva-spampot
COPY . /home/shiva-spampot/receiver/
RUN chown -R shiva-spampot:shiva-spampot /home/shiva-spampot/

USER shiva-spampot

RUN python3 -m venv receiver

RUN receiver/bin/pip install wheel && \
    receiver/bin/pip install -r receiver/requirements.txt

RUN cp receiver/config.ini.example receiver/config.ini

ENV SHIVA_HOST=0.0.0.0
EXPOSE 2525/tcp

CMD ["receiver/bin/python3", "receiver/run_server.py"]