# Created by: Michael Klements
# Updated by: Andrew Cliff
# For Raspberry Pi Desktop Case with OLED Stats Display using the SH1106 OLED display
# Based on Luma OLED libraries
# Dependencies are luma, psutil and pillow.  All these can be installed using "pip3 install xxxx" where xxxx is the dependency
# Installation & Setup Instructions - https://www.the-diy-life.com/add-an-oled-stats-display-to-raspberry-pi-os-bullseye/

#!/usr/bin/python3
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import psutil as PS
import socket
from time import sleep
import board
import digitalio

from PIL import ImageFont

import subprocess

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

KB=1024
MB=KB*1024
GB=MB*1024

# Examples for usage:
#    IP = get_ipv4_from_interface("eth0")
#    IP = get_ipv4_from_interface("wlan0")
def get_ipv4_from_interface(interfacename):
    res="IP ?"
    try:
        iface=PS.net_if_addrs()[interfacename]
        for addr in iface:
            if addr.family is socket.AddressFamily.AF_INET:
                return "IP {0}".format(addr.address)
    except:
        return res
    return res

# This looks for the first IPv4 address that is not on the
# loopback interface. There is no guarantee on the order of
# the interfaces in the enumeration. If you've multiple interfaces
# and want to ensure to get an IPv4 address from a dedicated adapter,
# use the previous method.
def get_ipv4():
    ifaces=PS.net_if_addrs()
    for key in ifaces:
        if (key!="lo"): # Ignore the loopback interface
            # if it's not loopback, we look for the first IPv4 address    
            iface = ifaces[key]
            for addr in iface:
                if addr.family is socket.AddressFamily.AF_INET:
                    return "IP {0}".format(addr.address)
    return "IP ?"


# Display Refresh
LOOPTIME = 10

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
device.clear()

FONTSIZE = 16

font = ImageFont.truetype('PixelOperator.ttf', FONTSIZE)
c = canvas(device)

top = 0
x = 2

while True:

    IP = get_ipv4()

    CPU = "CPU {:.1f}%".format(round(PS.cpu_percent(),1))

    temps=PS.sensors_temperatures()
    Temp= "{:.1f}°C".format(round(temps['cpu_thermal'][0].current,1))

    mem=PS.virtual_memory()
    MemUsage = "Mem {:5d}/{:5d}MB".format(round((mem.used+MB-1)/MB),round((mem.total+MB-1)/MB))

    root=PS.disk_usage("/")
    Disk="Disk {:4d}/{:4d}GB".format(round((root.used+GB-1)/GB),round((root.total+GB-1)/GB))

    # Pi Stats Display
    with c as draw:
        draw.rectangle(device.bounding_box, outline=0, fill=0)
        draw.text((x, top), IP, font=font, fill=255)
        draw.text((x, top+FONTSIZE), CPU, font=font, fill=255)
        draw.text((x+80,top+FONTSIZE), Temp, font=font, fill=255)
        draw.text((x, top+2*FONTSIZE), MemUsage, font=font, fill=255)
        draw.text((x, top+3*FONTSIZE), Disk, font=font, fill=255)
   
    sleep(LOOPTIME)