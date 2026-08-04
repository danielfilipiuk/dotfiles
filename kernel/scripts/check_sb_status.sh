#!/bin/bash

sbverify --list /boot/vmlinuz-$(uname -r)

openssl x509 -in /etc/sb/keys/MOK.crt -noout -subject

mokutil --sb-state

bootctl status

