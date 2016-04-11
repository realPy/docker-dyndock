#!/bin/sh

IP=$(ip route|awk '/src/ { print $9 }')
GW=$(ip route|awk '/via/ { print $3 }')


echo "$IP"> /etc/dnscache/env/IP
echo "nameserver $IP"> /etc/resolv.conf

/usr/bin/tinydnsdyn &

(nc $GW 3333 <&- | /eventListener.sh ) &
/usr/bin/svscanboot
