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

class radio:
    def __init__(self, my_server_ip, my_radio_id):
        self.led = LED(6)                   # Enlightens the radio dial
        self.amp = LED(16)                  # The relay that operates the class-D amp
        self.power = Button(5)              # On-off switch
        self.select1 = Button(25)           # Connected to a rotary switch (output 1)
        self.select2 = Button(12)           #                              (output 2)
        self.select3 = Button(26)           #                              (output 3)
        self.server = LmsServer(my_server_ip)
        self.connected = False
        print('Searching for playerid=' + my_radio_id)
        players = self.server.cls_players_list()
        for self.player in players:
            if self.player["playerid"] == my_radio_id:
                self.server.cls_player_on_off(self.player["playerid"], 0)
                print("Player " + self.player["playerid"] + " turned off")
                self.connected = True
                break

    def on(self):
        self.led.on()
        self.amp.on()
        self.server.cls_player_on_off(self.player["playerid"], 1)
        player_status = self.server.cls_player_status(self.player["playerid"])
        if player_status['mode'] != "play":
            if player_status['playlist_tracks'] >= 1:
                self.server.cls_player_stop(self.player["playerid"])
                self.server.cls_player_play(self.player["playerid"])

    def off(self):
        self.server.cls_player_on_off(self.player["playerid"], 0)
        self.amp.off()
        self.led.off()

    def error(self):
        self.led.blink(background=False)

my_radio = radio(getenv("SB_SERVER", "192.168.1.94:9000"), getenv("SB_PLAYER_ID", get_mac_address()))
if my_radio.connected:
    power_prev_state = 0
    while True:
        power_state = my_radio.power.is_pressed
        if power_state != power_prev_state:
            power_prev_state = power_state
            if power_state == 0:        # Switch off
                print("Switch off detected")
                my_radio.off()
            else:                       # Switch on
                print("Switch on detected")
                my_radio.on()
        sleep(0.2)
else:
    print('Error: Radio initialization failed')
    my_radio.error()