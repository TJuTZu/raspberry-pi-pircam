raspberry-pi-pircam.py
======================

Raspberry Pi motion detection IR Camera with IR Led by TJuTZu
-------------------------------------------------------------


raspberry-pi-pircam-py is for controlling Raspberry Pi camera module
with PIR motion detector


Requirement
-----------

Raspberry Pi
Camera module
PIR


GPIO usage
----------------------
#         1  2 PIR 5v
#         3  4
#         5  6 PIR GND
# PIR IN  7  8
#         9  10
#         11 12 IRLED OUT
#         13 14 IRLED GND
#         15 16
#         17 18
#         19 20
#         21 22
#         23 24
#         25 26
#
# PIR IN (7) = GPIO 4
# PIR OUT (12) = GPIO 18
