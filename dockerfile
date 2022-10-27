FROM ubuntu:20.04

# use bash shell as default
SHELL ["/bin/bash", "-c"]

# disable questions
ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# install python, pip and pipenv
RUN apt-get update && \
    apt-get install -y curl gcc make git net-tools systemd python3.9 python3-pip

# install mariadb-server
RUN apt-get install -y mariadb-server

RUN pip install --upgrade pip pipenv

# stay on user root to allow test.py to reinstall the database on every test
USER root
WORKDIR /home/motoko/work

COPY ./Pipfile /home/motoko/work/Pipfile
RUN pipenv install

# set some local environment variables
ENV LANG en_US.UTF-8

SHELL ["/bin/bash", "-lc"]

