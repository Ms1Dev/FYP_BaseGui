#!/bin/bash

sudo systemctl stop wpa_supplicant.service
sudo systemctl stop NetworkManager.service
sudo ifconfig wlan0 down
sudo ifconfig wlan0 192.168.4.1 up
sudo systemctl restart isc-dhcp-server.service
sudo systemctl restart hostapd.service