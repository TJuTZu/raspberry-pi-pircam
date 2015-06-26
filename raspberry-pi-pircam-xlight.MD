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
#         19 20 IRLIGHT GND
#         21 22
#         23 24 
#         25 26 
#
# PIR IN (7)  = GPIO 4
# IR OUT (12) = GPIO 18
# IR OUT (18) = GPIO 24
#
# Pinouts:
# http://raspi.tv/wp-content/uploads/2014/07/Raspberry-Pi-GPIO-pinouts.png
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
1.3 Changed logging since recording sometimes hangs and I try to figura what is wrong with the code
    - Changed date time used in filenames so that it doesn't contain separators
    - Changed log file name
    - Added 1 sec wait so that every recording is at least 1 second long
1.4 Added little more logging
    - Added logging to find out why recording sometimes hangs
    - Corrected couple headings