# -------------------------------------------------------------------------------------------------
#
# raspberry-pi-pircam.py ver 1.2
#
# Raspberry Pi motion detection IR Camera with extra IR Led
# by TJuTZu
#
# Thanks to (I really can't name all) the people whose code I have used as a base
#
# MP4Box is used for video conversion to install
#  sudo apt-get update
#  sudo apt-get install gpac
#
# -------------------------------------------------------------------------------------------------


# Time handling
import time
from datetime import datetime

import StringIO
import subprocess
import os
from subprocess import call

# Raspberry Pi camera 
import picamera

# for debug
import logging

# -------------------------------------------------------------------------------------------------
#For GPIO
import RPi.GPIO as GPIO
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
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()
GPIO.setwarnings(False)

GPIO.setup(4, GPIO.IN)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, False)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, False)

# -------------------------------------------------------------------------------------------------
## Setup
# File
debug = True # True / False

# File
# filepath = "/home/pi/cam"
filepath = "/var/www/cam"
filenamePrefix = "PIR"
diskSpaceToReserve = 1024 * 1024 * 1024 # Keep 1024 mb free on disk

# Capture
RecordingOn   = False
bLedOn = False # True / False  

# Still Values
# 
RPiStillQuality = "70"
RPiExposure = "auto" # auto,night,nightpreview,backlight,spotlight,sports,snow,beach,verylong,fixedfps,antishake,fireworks

# -------------------------------------------------------------------------------------------------
# Disk space handling
# Original code by brainflakes
# www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235
# -------------------------------------------------------------------------------------------------

# Get available disk space
def getFreeSpace():
    st = os.statvfs(".")
    du = st.f_bavail * st.f_frsize
    #if debug == True: logging.debug("Free space %s" % du)
    return du

# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(filepath + "/")):
            if filename.startswith(filenamePrefix):
                os.remove(filepath + "/" + filename)
                logging.debug ("Deleted %s/%s to avoid filling disk" % (filepath,filename))
                if (getFreeSpace() > bytesToReserve):
                    return
                    
# -------------------------------------------------------------------------------------------------
# Generate date text
# -------------------------------------------------------------------------------------------------
def DateText():
    dt = datetime.now()
    text = "%04d.%02d.%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) 
    return text 

# -------------------------------------------------------------------------------------------------
# IR Light on/off
# -------------------------------------------------------------------------------------------------
def IRLight(onoff):
	# Addon IR LED
	GPIO.output(18, onoff)
	# External IR light
	GPIO.output(24, onoff)

# -------------------------------------------------------------------------------------------------
# Action to take when movement is detected by PIR
# I have connected PIR into GPIO channel 4
# -------------------------------------------------------------------------------------------------
def StartVideoRecording(camera, filename):
        
    logging.debug ("Movement detected!")
    
    # Turn IR Led on
    IRLight(True)

    if bLedOn: camera.led = True

    # Set file extension
    filename = filename + ".h264"
    #logging.debug("before")
    camera.start_recording(filename, format='h264')
    #logging.debug("after")

    logging.debug ("Video start %s" % filename)
       
    if bLedOn: camera.led = False

     
# -------------------------------------------------------------------------------------------------
# Action to take when movement has stopped
# -------------------------------------------------------------------------------------------------

def StopVideoRecording(camera):
    camera.stop_recording()
    logging.debug ("Video stop")
    IRLight(False)
    if bLedOn: camera.led = False

# -------------------------------------------------------------------------------------------------
# convert h264 stream to mp4 and remove not needed files
# MP3Box is used
# -------------------------------------------------------------------------------------------------
def conver_to_mp4(filename):
    
    command_ro_run = "MP4Box -add " + filename + ".h264 " +  filename + ".mp4"
    if debug == True: logging.debug (command_ro_run)
    subprocess.call(command_ro_run, shell=True)
    
    command_ro_run = "remove: " + filename + ".h264 "
    if debug == True: logging.debug (command_ro_run)
    os.remove(filename + ".h264")
   
# -------------------------------------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------------------------------------

with picamera.PiCamera() as camera:

    # for debug
    logfile = filepath + "/cam-" + DateText() + ".log"
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=logfile,level=logging.DEBUG)
    logging.debug ("Logs to: %s" % logfile)
    
    camera.led = False
    #camera.resolution = (1920, 1080)
    #camera.resolution = (1280, 720)
    camera.exposure_compensation = 2
    camera.exposure_mode = 'auto' # auto sports
    camera.meter_mode = 'matrix'
    camera.image_effect = 'none'
    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2014 PAJAT'
    camera.exif_tags['EXIF.UserComment'] = 'Raspberry Pi - PRICam.py Motion detection'
    
    logging.debug ("Capturing mode video")
     
    try:
        while True:
            #camera.wait_recording(1)
            time.sleep(0.01)
            if GPIO.input(4):
                # Check that enough free space is available 
                keepDiskSpaceFree(diskSpaceToReserve)
                # Not recording yet
                if RecordingOn == False:    
                    # Set filename 
                    dt = datetime.now()
                    filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                    # star recording
                    StartVideoRecording(camera, filename)
                    # set recording on
                    RecordingOn = True
                else:
                     camera.wait_recording(0)
            # movement stopped
            else:
                # was recording
                if RecordingOn == True:
                    # stop recording
                    StopVideoRecording(camera)
                    # set recording off
                    RecordingOn = False
                    # convert h264 to mp4
                    conver_to_mp4(filename)

    # Cleanup if stopped by using Ctrl-C
    except KeyboardInterrupt:
        logging.debug("Cleanup")
        GPIO.cleanup()
