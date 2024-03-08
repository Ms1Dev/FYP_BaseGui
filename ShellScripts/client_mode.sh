#!/bin/bash

sudo systemctl stop isc-dhcp-server.service
sudo systemctl stop hostapd.service
sudo systemctl restart wpa_supplicant.service
sudo systemctl restart NetworkManager.service
sudo systemctl restart networking.service