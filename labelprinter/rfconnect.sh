#!/bin/bash

echo "Killing old connection"
rfcomm release 1
hciconfig hci0 down
hciconfig hci0 up
echo "Connecting..."
result=$(rfcomm connect 1 D1:9B:AA:10:D7:5E 2>&1)
echo $result
while [[ $result =~ "down" ]]; do
    echo "Reconnecting..."
    sleep 1
    result=$(rfcomm connect 1 D1:9B:AA:10:D7:5E 2>&1)
    echo $result
done
chmod 666 /dev/rfcomm1