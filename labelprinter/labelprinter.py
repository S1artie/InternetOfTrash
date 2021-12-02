#!/usr/bin/python3

import getopt, sys, os, subprocess, time, cgi

from PIL import Image, ImageDraw, ImageFont

firstLine = sys.argv[1] if len(sys.argv) > 1 else ""
secondLine = sys.argv[2] if len(sys.argv) > 2 else ""
copies = int(sys.argv[3]) if len(sys.argv) > 3 else 1

cgiArgs = cgi.parse()
if 'firstLine' in cgiArgs:
    firstLine = cgiArgs['firstLine'][0]
if 'secondLine' in cgiArgs:
    secondLine = cgiArgs['secondLine'][0]
if 'copies' in cgiArgs:
    copies = int(cgiArgs['copies'][0])

safetyPre = 120
safetyPost = 2
distance = 8

fontSmall = ImageFont.truetype(font = "Helvetica.ttf", size = 30)
fontMedium = ImageFont.truetype(font = "Helvetica.ttf", size = 50)
fontBig = ImageFont.truetype(font = "Helvetica.ttf", size = 60)

image = Image.new('RGB', (10000, 384), color = 'white') # 384 height is only for printer protocol, actual print height is about 100 pixels
printHeight = 100


d = ImageDraw.Draw(image)
if firstLine and secondLine:
    width1, height1 = fontMedium.getsize(firstLine)
    width2, height2 = fontSmall.getsize(secondLine)
    width = max(width1, width2)
    d.text((safetyPre + ((width - width1) / 2), (printHeight - (height1 + height2 + distance)) / 2), firstLine, fill = (0,0,0), font = fontMedium)
    d.text((safetyPre + ((width - width2) / 2), ((printHeight - (height1 + height2 + distance)) / 2) + height1 + distance), secondLine, fill = (0,0,0), font = fontSmall)
    image = image.crop((0, 0, width + safetyPre + safetyPost, image.height))
else:
    width, height = fontBig.getsize(firstLine)
    d.text((safetyPre, (printHeight - height) / 2), firstLine, fill = (0,0,0), font = fontBig)
    image = image.crop((0, 0, width + safetyPre + safetyPost, image.height))

# Rotate 90 degrees and convert to b/w
image = image.transpose(Image.ROTATE_90)
image = image.convert(mode='1', dither=Image.NONE)

#image.save('out.png')

# Connect the bluetooth device
process = subprocess.Popen(['sudo', 'bash', 'rfconnect.sh'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Give the process a few secs to make the connection (we don't actually know if it works, the process does not terminate)
time.sleep(4)

# Open the device file
device = open("/dev/rfcomm1", "wb")

# The following code actually creates the printer commands
def print_header():
    device.write(b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04')
    return

def print_marker(lines=0x100):
    device.write(0x761d.to_bytes(2, 'little'))
    device.write(0x0030.to_bytes(2, 'little'))
    device.write(0x0030.to_bytes(2, 'little'))
    device.write((lines - 1).to_bytes(2, 'little'))
    return

def print_footer():
    device.write(b'\x1b\x64\x02')
    device.write(b'\x1b\x64\x02')
    device.write(b'\x1f\x11\x08')
    device.write(b'\x1f\x11\x0e')
    device.write(b'\x1f\x11\x07')
    device.write(b'\x1f\x11\x09')
    return

def print_line(image, line):
    for x in range(int(image.width / 8)):
        byte = 0
        for bit in range(8):
            if image.getpixel((x * 8 + bit, line)) == 0:
                byte |= 1 << (7 - bit)
        # 0x0a breaks the rendering
        # 0x0a alone is processed like LineFeed by the printe
        if byte == 0x0a:
            byte = 0x14
        device.write(byte.to_bytes(1, 'little'))
    return



for copy in range(copies):
    remaining = image.height
    line=0
    print_header()
    while remaining > 0:
        lines = remaining
        if lines > 256:
            lines = 256
        print_marker(lines)
        remaining -= lines
        while lines > 0:
            print_line(image, line)
            lines -= 1
            line += 1
    print_footer()

# Close the connection, kill the rfcomm process
device.close()
try:
    process.kill()
except PermissionError:
    pass

print("Content-Type: text/plain")
print()
print("success!")