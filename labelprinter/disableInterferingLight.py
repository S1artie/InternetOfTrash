#!/usr/bin/python3

import requests

requests.post(url = "http://homematic-raspi:2001/", data = "<methodCall><methodName>setValue</methodName><params><param><value><string>NEQ0399036:1</string></value></param><param><value><string>STATE</string></value></param><param><value><string>0</string></value></param></params></methodCall>")

print("Content-Type: text/plain")
print()
print("success!")