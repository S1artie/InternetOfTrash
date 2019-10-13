import blescan
import sys
import time

import bluetooth._bluetooth as bluez

BEACON_RESTMUELL = "fd:37:91:59:11:fa"
BEACON_BIO = "fd:37:91:59:11:fb"
BEACON_PAPIER = "fd:37:91:59:11:fe"
BEACON_RECYCLING1 = "fd:37:91:59:11:fc"
BEACON_RECYCLING2 = "fd:37:91:59:11:fd"

BEACONS_ALL = [BEACON_RESTMUELL, BEACON_BIO, BEACON_PAPIER, BEACON_RECYCLING1, BEACON_RECYCLING2]

BEACON_TIMEOUT = 30

beaconsPresent = {}

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print("BLE Reading started")

except:
    print("Error accessing Bluetooth device")
    sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

while True:
    beaconList = blescan.parse_events(sock, 10)
    timestamp = time.time()
    for beacon in beaconList:
        address, data, _, _, _, rssi = beacon.split(',')
        strength = 127 + int(rssi)
        if address in BEACONS_ALL:
            if not address in beaconsPresent:
                print("Found new beacon: " + address)
            beaconsPresent[address] = time.time()
    for beaconAddress, beaconTimestamp in beaconsPresent.items():
        if beaconTimestamp < timestamp - BEACON_TIMEOUT:
            print("Beacon removed: " + beaconAddress)
            del beaconsPresent[beaconAddress]


        

