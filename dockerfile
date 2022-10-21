FROM python:3.9 as build-base

# use bash shell as default
SHELL ["/bin/bash", "-c"]

# disable questions
ARG DEBIAN_FRONTEND=noninteractive

# install python, pip and pipenv
RUN apt-get update && \
    apt-get install -y sudo curl gcc make git mariadb-server net-tools

RUN pip install --upgrade pip pipenv

# add the user Motoko, tribute to https://en.wikipedia.org/wiki/Motoko_Kusanagi
RUN useradd --create-home --shell /bin/bash --no-log-init --system -u 999  motoko && \
	echo "motoko	ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers

USER motoko
WORKDIR /home/motoko

# set some local environment variables
ENV LANG en_US.UTF-8

SHELL ["/bin/bash", "-lc"]

