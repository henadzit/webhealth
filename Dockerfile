FROM ubuntu:14.04
MAINTAINER Henadzi Tsaryk (henadzit@)

USER root
RUN apt-get update && \
  apt-get install -y git \
  python \
  python-dev \
  python-pip \
  libmysqlclient-dev
RUN groupadd -r nonroot && \
  useradd -r -g nonroot -d /home/nonroot -s /sbin/nologin -c "Nonroot User" nonroot && \
  mkdir /home/nonroot && \
  chown -R nonroot:nonroot /home/nonroot


USER nonroot
WORKDIR /home/nonroot
RUN git clone https://github.com/henadzit/webhealth

USER root
WORKDIR /home/nonroot/webhealth
RUN pip install -r requirements.txt
RUN export PYTHONPATH=$(pwd)
CMD python bin/webhealth_runner.py --website-file similarweb-sites.txt