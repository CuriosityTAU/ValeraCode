#!/bin/bash
cd /home/odroid/Code/valera-code/
echo "odroid" | sudo -S chmod 666 /dev/gpiochip0 /dev/gpiochip1
echo "odroid" | sudo -S chmod 666 /dev/i2c-0 /dev/i2c-1 /dev/i2c-2

cd notebooks
python3 startup.py
