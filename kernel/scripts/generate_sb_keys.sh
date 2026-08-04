#!/bin/bash

cd /etc/sb/keys
sudo openssl req -new -x509 -newkey rsa:2048 -keyout MOK.key -out MOK.crt -nodes -days 36500 -subj "/CN=Polaris_Custom_GNU-Linux_Kernel/"
sudo openssl x509 -in MOK.crt -outform DER -out MOK.der
sudo mokutil --import /root/secureboot/MOK.der
