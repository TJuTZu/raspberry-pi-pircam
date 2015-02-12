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
External IP Light

GPIO usage
# -------------------------------------------------------------------------------------------------
#         1  2 PIR 5v
#         3  4
#         5  6 PIR GND
# PIR IN  7  8
#         9  10
#         11 12 IRLED OUT
#         13 14 IRLED GND
#         15 16
#         17 18 IRLIGHT OUT
#         19 20 IRLIGHT OUT
#         21 22
#         23 24 
#         25 26 
#
# PIR IN (7) = GPIO 4
# PIR OUT (12) = GPIO 18
# -------------------------------------------------------------------------------------------------


Changes:
--------

1.0 Original version
1.1 Removed incomplete still images part from the code and changed default output folder under www
1.2 Added logging
    - all prints replaced by logging
    - PrintDebug(): revoved
    - DateText(): function added to be used for date string creation
    - Function GPIO_04_Rise(camera, filename): renamed to StartVideoRecording(camera, filename):
    - Function GPIO_04_Fall(camera): renamed to StopVideoRecording(camera):
    - Calling rm replased with os.remove in convert_to_mp4()