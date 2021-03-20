#!/usr/bin/env python3

"""
PITSF

This program is designed to operate a vintage radio device turned into a
Logitech Media Server player, using a Raspberry Pi, Squeezelite, soundcard,
amp, leds plus a fiew controls (pots and switches).

Environment variables:
    SB_SERVER: Server address plus port (example: 192.168.1.94:9000) (default: 127.0.0.1:9000)
    SB_PLAYER_ID: Player Id (MAC address) (default: host MAC address)

2021-03-20 : V0.1. Turning the radio on/off works.
"""

from os import getenv
from sys import exit
from time import sleep
from getmac import get_mac_address
from gpiozero import LED
from gpiozero import Button
from lmsmanager import LmsServer

led = LED(6)                        # Enlightens the radio dial
amp = LED(16)                       # The relay that operates the class-D amp
power = Button(5)                   # An on-off switch
select1 = Button(25)                # Connected to a rotary switch (output 1)
select2 = Button(12)                #                              (output 2)
select3 = Button(26)                #                              (output 3)

my_server = LmsServer(getenv("SB_SERVER", "127.0.0.1:9000"))
my_player_id = getenv("SB_PLAYER_ID", get_mac_address())

power_prev_state = 0
while True:
    power_state = power.is_pressed
    if power_state != power_prev_state:
        power_prev_state = power_state
        if power_state == 0:        # Switch off
            led.off()
            amp.off()
            my_server.cls_player_on_off(my_player_id, 0)
        else:                       # Switch on
            led.on()
            amp.on()
            my_server.cls_player_on_off(my_player_id, 1)
    sleep(0.2)