#!/bin/bash

GW=`ip route|awk '/via/ { print $3 }'`


while read line
do
ID=`echo $line | awk '{print $2}' | head -c-2`
STATE=`echo $line | awk '{print $5}'`
echo $line >> /tmp/test

if [ $STATE == "attach" -o $STATE == "create" ]
then
   NAME=`curl -s http://$GW:2376/containers/$ID/json | /JSON.sh | egrep '\["Name"]' | cut -f 2 | sed -e 's/"\/\(.*\)"/\1/'`
   IP=`curl -s http://$GW:2376/containers/$ID/json | /JSON.sh | egrep '\["NetworkSettings"]' | sed -e 's/.*IPAddress\":\"\([^"]*\).*/\1/'`
   IDHASH=`echo "$ID" | md5sum | awk '{print $1}'`
   if [ $NAME != "" ]
   then
   	RESULT=`curl "http://root:root@localhost/?hostname=$NAME.docker&myip=$IP&uuid=$IDHASH.docker"`
   fi
fi

if [ $STATE == "destroy" -o $STATE == "die"  ]
then
   #we dont known the name only the ID but the have IDHASH :)
   IDHASH=`echo "$ID" | md5sum | awk '{print $1}'`
   DOMAINNAME=`dig +time=0 +tries=0 +short $IDHASH.docker TXT | cut -d "\"" -f2` 
   RESULT=`curl "http://root:root@localhost/delete?hostname=$DOMAINNAME"`
   RESULT=`curl "http://root:root@localhost/delete?hostname=$IDHASH.docker"`
fi

done < "${1:-/dev/stdin}"

