#!/bin/bash

GW=`ip route|awk '/via/ { print $3 }'`


while true;
do
nc $GW 3333 | while read line
do
ID=`echo $line | awk '{print $2}' | head -c-2`
STATE=`echo $line | awk '{print $5}'`
echo $line 

/manage.sh $GW $STATE $ID&

done

done
