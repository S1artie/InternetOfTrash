# -*- coding: utf-8 -*-
import blescan
import sys
import time
import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from yattag import Doc, indent
import re
from xml.dom import minidom

import bluetooth._bluetooth as bluez

BEACON_RESTMUELL = "fd:37:91:59:11:fa"
BEACON_BIO = "e2:c2:c6:a4:d1:6f"
BEACON_PAPIER = "c3:24:a0:eb:ea:cd"
BEACON_RECYCLING1 = "cc:ca:10:35:6b:f4"
BEACON_RECYCLING2 = "e6:a3:14:18:7d:bf"
BEACONS_ALL = [BEACON_RESTMUELL, BEACON_BIO, BEACON_PAPIER, BEACON_RECYCLING1, BEACON_RECYCLING2]
BEACON_TIMEOUT = 90

EVENT_RESTMUELL = "Restmülltonne"
EVENT_RECYCLING = "Wertstofftonne"
EVENT_BIO = "Biotonne"
EVENT_PAPIER = "Papiertonne"
EVENT_POLLING_INTERVAL = 86400

MIN_FILE_UPDATE_INTERVAL = 60

TEMP_UPDATE_INTERVAL = 300
FORECAST_UPDATE_INTERVAL = 1800

def mainLoop():
    global lastEventPolling
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        print("BLE Reading started")
    except:
        print("Error accessing Bluetooth device")
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
    
    beaconsPresent = {}
    eventsByDate = {}
    lastEventPolling = 0
    lastTodayString = ""
    lastFileUpdate = 0
    lastTempUpdate = 0
    lastForecastUpdate = 0
    tempOutside = "-"
    tempCooler = "-"
    tempForecastLow = "-"
    tempForecastHigh = "-"
    tempForecastTarget = "heute"

    while True:
        timestamp = time.time()
        anythingChanged = False
        if timestamp - EVENT_POLLING_INTERVAL > lastEventPolling:
            newEvents = requestAndParseCalendar()
            if not newEvents is None:
            	eventsByDate = newEvents
            lastEventPolling = timestamp
            anythingChanged = True
            
        today = datetime.now()
        todayString = today.strftime("%Y-%m-%d")
        if lastTodayString != todayString:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            print("Todays' date has changed to " + todayString)
            lastTodayString = todayString
            anythingChanged = True
            
        if (timestamp - lastTempUpdate) >= TEMP_UPDATE_INTERVAL:
            newTempOutside = requestTemperatureSensor(2)
            newTempCooler = requestTemperatureSensor(1)
            if tempOutside != newTempOutside or tempCooler != newTempCooler:
                tempOutside = newTempOutside
                tempCooler = newTempCooler
                print("Temperatures changed to outside: " + tempOutside + ", cooler: " + tempCooler)
                anythingChanged = True
            lastTempUpdate = timestamp
        
        if (timestamp - lastForecastUpdate) >= FORECAST_UPDATE_INTERVAL:
            tempForecast = requestTemperatureForecast()
            if tempForecast:
                tempForecastLow = str(tempForecast[0])
                tempForecastHigh = str(tempForecast[1])
                tempForecastTarget = tempForecast[2]
                anythingChanged = True
            lastForecastUpdate = timestamp
        
        beaconList = blescan.parse_events(sock, 10)
        for beacon in beaconList:
            address, data, _, _, _, rssi = beacon.split(',')
            strength = 127 + int(rssi)
            if address in BEACONS_ALL:
                if not address in beaconsPresent:
                    print("Found new beacon: " + address)
                    anythingChanged = True
                beaconsPresent[address] = time.time()
        for beaconAddress, beaconTimestamp in beaconsPresent.items():
            if beaconTimestamp < timestamp - BEACON_TIMEOUT:
                print("Beacon removed: " + beaconAddress)
                del beaconsPresent[beaconAddress]
                anythingChanged = True
        
        if anythingChanged or (timestamp - lastFileUpdate) >= MIN_FILE_UPDATE_INTERVAL:
            writeOutput(eventsByDate, beaconsPresent, today, tempOutside, tempCooler, tempForecastLow, tempForecastHigh, tempForecastTarget)
            lastFileUpdate = timestamp
        

        
def requestCalendar():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Referer': 'https://www.muellmax.de/abfallkalender/rsa/res/RsaStart.php',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    data = {
        'mm_ses': 'NW95K3lZaEpxNDBsM3JYZGNMalRjRzFGUkZPU0hBWWpBVzEzUnZQMlErdlVBUFVqcGtRcEFNM3IvNTJvR1FNaUVINlpYaEYrR29JUm9NblhmM3Z1U2x0ZmpBWjNadzg1Wk5MMXZMVkRmK2hKcHhycEtET0thV0l5c01nWmsvbi9nWTlsRFBkV0ZWU0tpUTVuZTVyWnJBdzFIS2lvVVFEaXQvckVLK2lsTFhLTEJyM1BDQ3dva28vb2p1TDBMcjFhem1pdUF5b2Qwa3A4SlUreW84cjZOeUN2UlMrcUJmdjdsT2h5WWNaVVdpaXhoanROVGhtUG9GMU54WE9aQ09SbkYxVGhPU2UyZi84SStYd2NxcmJSa3lXeFVVMElkN29XUHQvalQ3bGErM009',
        'xxx': '1',
        'mm_frm_type': 'termine',
        'mm_frm_fra_RM4T': 'RM4T',
        'mm_frm_fra_BIO1T': 'BIO1T',
        'mm_frm_fra_PAT': 'PAT',
        'mm_frm_fra_WET': 'WET',
        'mm_ica_gen': 'iCalendar-Datei laden'
    }
    response = requests.post('https://www.muellmax.de/abfallkalender/rsa/res/RsaStart.php', headers=headers, data=data)
    return response

def parseCalendar(calendar):
    newEvents = {}
    gcal = Calendar.from_ical(calendar)
    for component in gcal.walk():
        if component.name == "VEVENT":
            date = component.get('dtstart').dt.strftime("%Y-%m-%d")
            if not date in newEvents:
                newEvents[date] = []
            summary = component.get('summary')
            if EVENT_RESTMUELL.decode('utf-8') in summary:
                newEvents[date].append(EVENT_RESTMUELL)
            elif EVENT_BIO in summary:
                newEvents[date].append(EVENT_BIO)
            elif EVENT_PAPIER in summary:
                newEvents[date].append(EVENT_PAPIER)
            elif EVENT_RECYCLING in summary:
                newEvents[date].append(EVENT_RECYCLING)
            else:
                print("Unknown calendar event found: " + summary)
    return newEvents

def requestAndParseCalendar():
    print("Requesting new trash collection calendar...")
    # First, query the trash collection service for an iCal file
    try:
        iCalResponse = requestCalendar()
    except:
        print("Got exception when requesting trash collection calendar")
        return;
    if iCalResponse.status_code != 200:
        print("Got error status code from trash collection calendar server: " + str(iCalResponse.status_code))
        return
    # Parse the file into trash collection events
    collectionEvents = parseCalendar(iCalResponse.content)
    if len(collectionEvents) == 0:
        print("Failed to find any collection dates in calendar - assuming error, working with old data")
        return
    else:
        print("Parsed {} collection dates from calendar".format(len(collectionEvents)))
        return collectionEvents
        
def findNextPickupDays(event, today, eventsByDate):
    for days in range(0,32):
        dateString = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        if dateString in eventsByDate and event in eventsByDate[dateString]:
            return days
    return "?"
        
def convertBeaconToEvent(beacon):
    if beacon == BEACON_RESTMUELL:
        return EVENT_RESTMUELL
    elif beacon == BEACON_BIO:
        return EVENT_BIO
    elif beacon == BEACON_PAPIER:
        return EVENT_PAPIER
    elif beacon == BEACON_RECYCLING1:
        return EVENT_RECYCLING
    elif beacon == BEACON_RECYCLING2:
        return EVENT_RECYCLING
        
def resolveLocationStatus(beacons, beaconsPresent):
    if all(elem in beaconsPresent for elem in beacons):
        return "hinter dem Haus"
    else:
        return "an der Straße"
        
def resolveAlertStatus(beacons, beaconsPresent, eventsByDate, today):
    todayString = today.strftime("%Y-%m-%d")
    tomorrowString = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if all(elem in beaconsPresent for elem in beacons):
        eventForBeacon = convertBeaconToEvent(beacons[0])
        if todayString in eventsByDate and eventForBeacon in eventsByDate[todayString]:
            return "pickupToday"
        elif tomorrowString in eventsByDate and eventForBeacon in eventsByDate[tomorrowString]:
            return "pickupTomorrow"
    return ""
        
def writeTrashcanOutput(event, eventType, beacons, eventsByDate, beaconsPresent, today, doc):
    doc.stag('trashcan', ('name', event), \
            ('type', eventType), \
            ('location', resolveLocationStatus(beacons, beaconsPresent)), \
            ('alert', resolveAlertStatus(beacons, beaconsPresent, eventsByDate, today)), \
            ('nextPickupDays', findNextPickupDays(event, today, eventsByDate)));
        
def writeOutput(eventsByDate, beaconsPresent, today, tempOutside, tempCooler, tempForecastLow, tempForecastHigh, tempForecastTarget):
    doc = Doc()
    with doc.tag('iot', ('timestamp', datetime.now().strftime('%d.%m.%Y %H:%M:%S'))):
        writeTrashcanOutput(EVENT_RESTMUELL, 1, [BEACON_RESTMUELL], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(EVENT_BIO, 2, [BEACON_BIO], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(EVENT_PAPIER, 3, [BEACON_PAPIER], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(EVENT_RECYCLING, 4, [BEACON_RECYCLING1, BEACON_RECYCLING2], eventsByDate, beaconsPresent, today, doc)
        doc.stag('temperatures', ('outside', tempOutside), ('cooler', tempCooler), ('forecastLow', tempForecastLow), ('forecastHigh', tempForecastHigh), ('forecastTarget', tempForecastTarget))
        
    outFile = open("out/trashcans.xml", "w")
    outFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outFile.write('<?xml-stylesheet type="text/xsl" href="transform.xsl" ?>\n')
    outFile.write(indent(doc.getvalue()))
    outFile.close()
	
	
def requestTemperatureSensor(sensorNumber):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = "<methodCall><methodName>getValue</methodName><params><param><value><string>NEQ0531830:" \
             + str(sensorNumber) + "</string></value></param><param><value><string>TEMPERATURE</string></value></param></params></methodCall>"
    try:
        response = requests.post('http://homematic-raspi:2001/', headers=headers, data=data)
    except:
        print("Got exception while querying Homematic CCU")
        return "-"
    if response.status_code != 200:
        print("Got error status code from Homematic CCU: " + str(response.status_code))
        return "-"
    else:
        parsed = re.search(r'<double>(-?\d+\.\d)\d*</double>', response.content, re.IGNORECASE)
        if parsed:
            return parsed.group(1)
        else:
            print("Got incomprehensible response from Homematic CCU: " + response.content)
            return "-"
            
            
def requestTemperatureForecast():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        response = requests.get('https://www.yr.no/sted/Tyskland/Nordrhein-Westfalen/Troisdorf/forecast_hour_by_hour.xml')
    except:
        print("Got exception when querying weather forecast")
        return None
    if response.status_code != 200:
        print("Got error status code from weather service: " + str(response.status_code))
        return None
    else:
        # Dynamically determine the hourly window during which to look at the temperatures
        # If past 17:00, look at tomorrows' window of 08:00 - 20:00. If before 17:00, look at todays'
        # of 08:00 - 20:00, but cut off the beginning if we are past 08:00.
        # This assumes the report being by the hour, starting at the current hour.
        hourOfDay = datetime.now().hour
        if hourOfDay < 17:
            forecastTarget = "heute"
            windowStart = max(8 - hourOfDay, 0)
            windowEnd = max((8 - hourOfDay) + 13, 1)
        else:
            forecastTarget = "morgen"
            windowStart = (24 - hourOfDay) + 8
            windowEnd = windowStart + 13
            
        xmldoc = minidom.parseString(response.content)
        hours = xmldoc.getElementsByTagName('time')
        lowestTemperature = 100
        highestTemperature = -100
        for i in range (windowStart, windowEnd):
            temperature = hours[i].getElementsByTagName('temperature')[0].attributes['value'].value
            try:
                temperature = int(temperature)
            except ValueError:
                temperature = -100
            if temperature > highestTemperature:
                highestTemperature = temperature;
            if temperature < lowestTemperature:
                lowestTemperature = temperature;
        if highestTemperature == -100:
            return None
        return [lowestTemperature, highestTemperature, forecastTarget]
            
        

# Open the bluetooth reading and enter a reading loop
mainLoop()
