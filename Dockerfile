# sshd
#
# VERSION               0.0.2

FROM ubuntu:14.04
MAINTAINER Tesla <tesla@v-ip.fr>

RUN apt-get update && apt-get install -y build-essential && apt-get install -y wget && apt-get install -y ucspi-tcp && apt-get install -y daemontools


RUN wget https://cr.yp.to/djbdns/djbdns-1.05.tar.gz
RUN tar xvfz djbdns-1.05.tar.gz
RUN echo gcc -O2 -include /usr/include/errno.h > djbdns-1.05/conf-cc
RUN cd djbdns-1.05;make setup check
RUN rm -rf /djbdns-1.05 && rm djbdns-1.05.tar.gz

RUN apt-get install -y curl

RUN useradd svclog && useradd dnscache && useradd tinydns
RUN dnscache-conf dnscache svclog /etc/dnscache
RUN tinydns-conf tinydns svclog /etc/tinydns 0.0.0.0


RUN touch /etc/dnscache/root/ip/172
RUN rm /etc/dnscache/root/ip/127.0.0.1
RUN echo "#!/bin/sh" > /etc/dnscache/log/run
RUN echo "exec setuidgid svclog multilog t '-*' '+* fatal: *' ./main" >> /etc/dnscache/log/run



RUN mkdir /service && ln -s /etc/dnscache /service/dnscache && ln -s /etc/tinydns /service/tinydns && ln -s /service/ /etc/service


COPY ./htpasswd /etc/tinydns/
RUN echo "127.0.0.1">/etc/dnscache/root/servers/docker
RUN echo "127.0.0.1">/etc/dnscache/root/servers/0.18.172.in-addr.arpa

RUN apt-get install -y python
RUN apt-get install -y dnsutils

COPY ./JSON.sh /
COPY ./eventListener.sh /
COPY ./docker-entrypoint.sh /
COPY ./tinydnsdyn /usr/bin/

EXPOSE 53:53
ENTRYPOINT ["/docker-entrypoint.sh"]
