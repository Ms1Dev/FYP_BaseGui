#!/bin/bash

systemctl stop isc-dhcp-server.service
systemctl stop hostapd.service
systemctl restart wpa_supplicant.service
systemctl restart NetworkManager.service
systemctl restart networking.service