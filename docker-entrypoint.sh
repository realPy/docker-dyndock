#!/bin/sh

IP=$(ifconfig eth0 | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)


echo "$IP"> /etc/dnscache/env/IP
echo "nameserver $IP"> /etc/resolv.conf

htpasswd -b -d -c /etc/tinydns/htpasswd $API_USER $API_PWD
/usr/bin/tinydnsdyn &

python /event.py&
/usr/local/bin/svscanboot 
