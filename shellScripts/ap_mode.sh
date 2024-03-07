#!/bin/bash

systemctl stop wpa_supplicant.service
systemctl stop NetworkManager.service
ifconfig wlan0 down
ifconfig wlan0 192.168.4.1 up
systemctl restart isc-dhcp-server.service
systemctl restart hostapd.service