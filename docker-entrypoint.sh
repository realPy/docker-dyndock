#!/bin/sh

IP=$(ifconfig eth0 | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)


echo "$IP"> /etc/dnscache/env/IP
echo "nameserver $IP"> /etc/resolv.conf

htpasswd -b -d -c /etc/tinydns/htpasswd $API_USER $API_PWD

if [ -n "$FORWARD" ];
then 
rm /etc/dnscache/root/servers/@
touch /etc/dnscache/root/servers/@
for i in $(echo $FORWARD | sed "s/,/ /g")
do
    # call your procedure/other scripts here below
    echo $i >> etc/dnscache/root/servers/@
done
chmod +t /etc/dnscache/root/servers/@
fi

/usr/bin/tinydnsdyn &
python /event.py&
/usr/local/bin/svscanboot 
