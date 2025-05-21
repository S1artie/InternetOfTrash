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
import sdnotify
import os

import bluetooth._bluetooth as bluez

n = sdnotify.SystemdNotifier()

BEACON_RESTMUELL = "d4:dd:1f:1f:52:08"
BEACON_BIO = "ee:0b:87:8d:c0:80"
BEACON_PAPIER = "f5:8f:c7:3a:7b:5a"
BEACON_RECYCLING = "da:32:c3:8f:39:ce"
#BEACON_RECYCLING2 = "fe:fe:82:66:d5:83"
BEACONS_ALL = [BEACON_RESTMUELL, BEACON_BIO, BEACON_PAPIER, BEACON_RECYCLING]
BEACON_TIMEOUT = 120

EVENT_RESTMUELL = "Restabfallbehaelter"
LABEL_RESTMUELL = "Restmülltonne"
EVENT_RECYCLING = "Gelbe Behaelter"
LABEL_RECYCLING = "Gelbe Tonne"
EVENT_BIO = "Bioabfallbehaelter"
LABEL_BIO = "Biotonne"
EVENT_PAPIER = "Papierbehaelter"
LABEL_PAPIER = "Papiertonne"
EVENT_POLLING_INTERVAL = 3600 * 24

MIN_FILE_UPDATE_INTERVAL = 60

TEMP_UPDATE_INTERVAL = 300

def mainLoop():
    global lastEventPolling
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        n.notify("READY=1")
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
    tempOutside = "-"

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
            newTempOutside = requestTemperatureSensor()
            if tempOutside != newTempOutside:
                tempOutside = newTempOutside
                print("Temperatures changed to outside: " + tempOutside)
                anythingChanged = True
            lastTempUpdate = timestamp
        beaconList = blescan.parse_events(sock, 10)
        for beacon in beaconList:
            address, data, _, _, _, rssi = beacon.split(',')
            strength = 127 + int(rssi)
            if address in BEACONS_ALL:
                if not address in beaconsPresent:
                    print("Found new beacon: " + address)
                    anythingChanged = True
                beaconsPresent[address] = time.time()
#            else:
#                print("Found unknown beacon: " + address + ", data: " + data)
        for beaconAddress, beaconTimestamp in beaconsPresent.items():
            if beaconTimestamp < timestamp - BEACON_TIMEOUT:
                print("Beacon removed: " + beaconAddress)
                del beaconsPresent[beaconAddress]
                anythingChanged = True
        
        if anythingChanged or (timestamp - lastFileUpdate) >= MIN_FILE_UPDATE_INTERVAL:
            writeOutput(eventsByDate, beaconsPresent, today, tempOutside)
            lastFileUpdate = timestamp

        n.notify("WATCHDOG=1")
        

        
def requestCalendar():
    # Start a session
    session = requests.Session()

    # Headers for session initialization
    headers_init = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www5.bonn.de/WasteManagementBonnOrange/WasteManagementServlet",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }

    # Perform session initialization request
    response_init = session.get(
        "https://www5.bonn.de/WasteManagementBonnOrange/WasteManagementServlet",
        headers=headers_init,
    )

    # Extract JSESSIONID
    cookies = session.cookies.get_dict()
    jsessionid = cookies.get("JSESSIONID")

    if not jsessionid:
        print("Failed to establish session and extract JSESSIONID.")
        exit()

    #print("Established session with JSESSIONID: {}".format(jsessionid))
    #print(response_init.text)

    # Headers for the additional POST request (CITYCHANGED)
    headers_citychanged = {
        "User-Agent": headers_init["User-Agent"],
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": headers_init["Accept-Language"],
        "Accept-Encoding": headers_init["Accept-Encoding"],
        "Content-Type": "text/plain; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www5.bonn.de",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": headers_init["Referer"],
        "Cookie": "JSESSIONID={}".format(jsessionid),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
    }

    # Form data for the CITYCHANGED request
    data_citychanged = {
        "Ajax": "TRUE",
        "AjaxOnPage": "false",
        "AjaxDelay": "0",
        "ApplicationName": "com.athos.nl.mvc.abfterm.CheckAbfuhrTermineParameterBusinessCase",
        "BuildNumber": "125482",
        "BuildTime": "2024-11-29 12:44",
        "Focus": "Ort",
        "ID": "",
        "InFrameMode": "FALSE",
        "IsLastPage": "false",
        "IsSubmitPage": "false",
        "Method": "GET",
        "ModulName": "",
        "NewTab": "default",
        "NextPageName": "",
        "PageName": "Lageadresse",
        "PageXMLVers": "1.1",
        "VerticalOffset": "0",
        "RedirectFunctionNachVorgang": "",
        "SessionId": jsessionid,  # Use extracted JSESSIONID
        "ShowMenue": "false",
        "SubmitAction": "CITYCHANGED",
        "Hausnummer": "",
        "Hausnummerzusatz": "",
        "Ort": os.environ["TRASH_COLLECTION_CITY"],
        "Strasse": "",
    }

    # Perform the CITYCHANGED POST request
    response_citychanged = session.post(
        "https://www5.bonn.de/WasteManagementBonnOrange/WasteManagementServlet",
        headers=headers_citychanged,
        data=data_citychanged,
    )

    #print("CITYCHANGED request status: {}".format(response_citychanged.status_code))
    #print(response_citychanged.text)

    # Headers for the first POST request
    headers_first = headers_init.copy()
    headers_first.update({
        "Origin": "https://www5.bonn.de",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "JSESSIONID={}".format(jsessionid),
    })

    # Form data for the first POST request
    data_first = {
        "Ajax": "false",
        "AjaxOnPage": "false",
        "AjaxDelay": "0",
        "ApplicationName": "com.athos.nl.mvc.abfterm.CheckAbfuhrTermineParameterBusinessCase",
        "BuildNumber": "125482",
        "BuildTime": "2024-11-29 12:44",
        "Focus": "Hausnummer",
        "ID": "",
        "InFrameMode": "FALSE",
        "IsLastPage": "false",
        "IsSubmitPage": "false",
        "Method": "GET",
        "ModulName": "",
        "NewTab": "default",
        "NextPageName": "",
        "PageName": "Lageadresse",
        "PageXMLVers": "1.1",
        "VerticalOffset": "0",
        "RedirectFunctionNachVorgang": "",
        "SessionId": jsessionid,  # Use extracted JSESSIONID
        "ShowMenue": "false",
        "SubmitAction": "forward",
        "Ort": os.environ["TRASH_COLLECTION_CITY"],
        "Strasse": os.environ["TRASH_COLLECTION_STREET"],
        "Hausnummer": os.environ["TRASH_COLLECTION_NUMBER"],
        "Hausnummerzusatz": "",
    }

    # Perform the first POST request
    response_first = session.post(
        "https://www5.bonn.de/WasteManagementBonnOrange/WasteManagementServlet",
        headers=headers_first,
        data=data_first,
    )

    #print("First request status: {}".format(response_first.status_code))
    #print(response_first.text)

    # Headers for the second POST request
    headers_second = headers_first.copy()
    headers_second.update({
        "X-Requested-With": "XMLHttpRequest",
    })

    # Form data for the second POST request
    data_second = {
        "Ajax": "TRUE",
        "AjaxOnPage": "false",
        "AjaxDelay": "0",
        "ApplicationName": "com.athos.kd.bonn.abfuhrtermine.AbfuhrTerminModel",
        "BuildNumber": "125482",
        "BuildTime": "2024-11-29 12:44",
        "Focus": "",
        "ID": "",
        "InFrameMode": "FALSE",
        "IsLastPage": "true",
        "IsSubmitPage": "false",
        "Method": "POST",
        "ModulName": "",
        "NewTab": "default",
        "NextPageName": "",
        "PageName": "Terminliste",
        "PageXMLVers": "1.1",
        "VerticalOffset": "0",
        "RedirectFunctionNachVorgang": "",
        "SessionId": jsessionid,  # Use extracted JSESSIONID
        "ShowMenue": "false",
        "SubmitAction": "filedownload_ICAL",
    }

    # Perform the second POST request
    response_second = session.post(
        "https://www5.bonn.de/WasteManagementBonnOrange/WasteManagementServlet",
        headers=headers_second,
        data=data_second,
    )

    #print("Second request status: {}".format(response_second.status_code))
    #print(response_second.text)

    return response_second


def parseCalendar(calendar):
    newEvents = {}
    try:
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
    except:
        print("Got exception when parsing trash collection calendar")
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
    elif beacon == BEACON_RECYCLING:
        return EVENT_RECYCLING
        
def resolveLocationStatus(beacons, beaconsPresent):
    if not all(elem in beaconsPresent for elem in beacons):
        return "hinter der Garage"
    else:
        return "an der Straße"
        
def resolveAlertStatus(beacons, beaconsPresent, eventsByDate, today):
    todayString = today.strftime("%Y-%m-%d")
    tomorrowString = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    hourOfDay = datetime.now().hour
    if not all(elem in beaconsPresent for elem in beacons):
        eventForBeacon = convertBeaconToEvent(beacons[0])
        if todayString in eventsByDate and eventForBeacon in eventsByDate[todayString] and hourOfDay <= 10:
            return "pickupToday"
        elif tomorrowString in eventsByDate and eventForBeacon in eventsByDate[tomorrowString]:
            hourOfDay = datetime.now().hour
            if hourOfDay >= 18:
                return "pickupTomorrowAlert"
            else:
                return "pickupTomorrow"
    return ""
        
def writeTrashcanOutput(event, eventType, beacons, eventsByDate, beaconsPresent, today, doc):
    doc.stag('trashcan', ('name', event), \
            ('type', eventType), \
            ('location', resolveLocationStatus(beacons, beaconsPresent)), \
            ('alert', resolveAlertStatus(beacons, beaconsPresent, eventsByDate, today)), \
            ('nextPickupDays', findNextPickupDays(event, today, eventsByDate)));
        
def writeOutput(eventsByDate, beaconsPresent, today, tempOutside):
    doc = Doc()
    with doc.tag('iot', ('timestamp', datetime.now().strftime('%d.%m.%Y %H:%M:%S'))):
        writeTrashcanOutput(LABEL_RESTMUELL, 1, [BEACON_RESTMUELL], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(LABEL_BIO, 2, [BEACON_BIO], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(LABEL_PAPIER, 3, [BEACON_PAPIER], eventsByDate, beaconsPresent, today, doc)
        writeTrashcanOutput(LABEL_RECYCLING, 4, [BEACON_RECYCLING], eventsByDate, beaconsPresent, today, doc)
        doc.stag('temperatures', ('outside', tempOutside))
        
    outFile = open("out/trashcans.xml", "w")
    outFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outFile.write('<?xml-stylesheet type="text/xsl" href="transform.xsl" ?>\n')
    outFile.write(indent(doc.getvalue()))
    outFile.close()
	
def requestTemperatureSensor():
    return "-"
	
        

# Open the bluetooth reading and enter a reading loop
mainLoop()
