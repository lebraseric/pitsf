#!/usr/bin/env python3

"""PITSF

This program is designed to operate a vintage radio device turned into a
Logitech Media Server player, using a Raspberry Pi, Squeezelite,
soundcard, amp, leds and some switches.

Environment variables:
    SB_SERVER: Server address plus port (example: 192.168.1.94:9000)
        (default: 127.0.0.1:9000)
    SB_PLAYER_ID: Player Id (MAC address) (default: host MAC address)

2021-03-20 : V0.1   Turning the radio on/off works.
2021-03-26 : V0.1.1 General oo overhaul, added Radio class.
                    Initialization bugs fixed.
"""

__version__ = '0.1.1'
__author__ = 'Eric Le Bras'

from sys import exit
from time import sleep
from os import getenv
from getmac import get_mac_address
from gpiozero import LED
from gpiozero import Button
from lmsmanager import LmsServer


class Radio:

    def on(self) -> None:
        """Powering-on callback method"""
        self.led.on()
        self.amp.on()       # Closes the relay powering the amp
        # Power-on the player
        self.server.cls_player_on_off(self.player['playerid'], 1)
        # Clear playlist and load the preset
        self.server.cls_player_playlist_clear(self.player['playerid'])
        self.server.cls_player_playlist_add(self.player['playerid'],
                                            'pitsf_preset1')
        # Get player status
        player_status = self.server.cls_player_status(self.player['playerid'])
        if player_status['mode'] != 'play':
            if player_status['playlist_tracks'] >= 1:
                # Play works only if preceded by stop
                self.server.cls_player_stop(self.player['playerid'])
                self.server.cls_player_play(self.player['playerid'])

    def off(self) -> None:
        """Powering-off callback method"""
        # Power-off the player
        self.server.cls_player_on_off(self.player['playerid'], 0)
        self.amp.off()      # Opens the relay powering the amp
        self.led.off()

    def error(self) -> None:
        """Visualy indicate an error (never ending method)"""
        self.led.blink(background=False)

    def __init__(self, my_server_ip: str, my_player_id: str):
        """Radio initialization sequence
        This is normally called at system startup, when the radio is
        plugged in.  We check that we can talk to the server and that
        the player is running and connected to the server.  The
        player is turned off.  Finaly we enter the event loop that
        handles buttons events.
        """
        self.led = LED(6)             # Enlightens the radio dial
        self.amp = LED(16)            # The relay that operates the class-D amp
        self.power = Button(5)        # On-off switch
        self.select1 = Button(25)     # Connected to a rotary switch (output 1)
        self.select2 = Button(12)     #                              (output 2)
        self.select3 = Button(26)     #                              (output 3)
        self.server = LmsServer(my_server_ip)
        self.connected = False
        print('Searching for playerid=' + my_player_id)
        players = self.server.cls_players_list()
        for self.player in players:
            if self.player['playerid'] == my_player_id:
                self.server.cls_player_on_off(self.player['playerid'], 0)
                print('Player ' + self.player['playerid'] + ' turned off')
                self.connected = True
                break
        if self.connected:
            power_prev_state = 0
            while True:
                power_state = self.power.is_pressed
                if power_state != power_prev_state:
                    power_prev_state = power_state
                    if power_state == 0:        # Power switch off
                        print('Switch off detected')
                        self.off()
                    else:                       # Power switch on
                        print('Switch on detected')
                        self.on()
                sleep(0.2)
        else:
            print('Error: Radio initialization failed')
            self.error()


if __name__ == '__main__':
    # Create Radio instance and enter forever loop
    my_radio = Radio(getenv('SB_SERVER', '192.168.1.94:9000'),
                     getenv('SB_PLAYER_ID', get_mac_address()))