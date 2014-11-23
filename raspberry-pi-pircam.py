# -------------------------------------------------------------------------------------------------
#
# raspberry-pi-pircam.py ver 1.0
#
# Raspberry Pi motion detection IR Camera with IR Led
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
#         17 18
#         19 20
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

# -------------------------------------------------------------------------------------------------
## Setup
# File
debug = True # True / False

# File
filepath = "/home/pi/cam"
filenamePrefix = "PIR"
diskSpaceToReserve = 1024 * 1024 * 1024 # Keep 1024 mb free on disk

# Capture
CapturingMode = "Video" # Still, Video
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
    #if debug == True: print("Free space %s" % du)
    return du

# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(filepath + "/")):
            if filename.startswith(filenamePrefix):
                os.remove(filepath + "/" + filename)
                print "Deleted %s/%s to avoid filling disk" % (filepath,filename)
                if (getFreeSpace() > bytesToReserve):
                    return
                    
# -------------------------------------------------------------------------------------------------
# Action to take when mevement is detected by PIR
# I have connected PIR into GPIO channel 4
# -------------------------------------------------------------------------------------------------
def PrintDebug():
    dt = datetime.now()
    YoTime = "%04d.%02d.%02d %02d:%02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond) 
    print (YoTime)



# -------------------------------------------------------------------------------------------------
# Action to take when movement is detected by PIR
# I have connected PIR into GPIO channel 4
# -------------------------------------------------------------------------------------------------
def GPIO_04_Rise(camera, filename):
        
    print ("Movement detected!")
    
    if debug == True: PrintDebug()
    
    # Turn IR Led on
    GPIO.output(18, True)

    if bLedOn: camera.led = True

    if CapturingMode == "Still":
             
        # Set file extension
        filename = filename + ".jpg"
       
        # Take picture

        if debug == True: PrintDebug()
            
        # Give the camera some time to adjust to conditions
        # time.sleep(0.1)
        camera.capture(filename)
      
        GPIO.output(18, False)

        print ("Picture taken %s" % filename)
       
    if CapturingMode == "Video":
        # Set file extension
        filename = filename + ".h264"
        #print("before")
        camera.start_recording(filename, format='h264')
        #print("after")

        if debug == True: PrintDebug()
            
        print ("Video start %s" % filename)
       
    if debug == True: PrintDebug()
    if bLedOn: camera.led = False

     
# -------------------------------------------------------------------------------------------------
# Action to take when mevement has stopped
# -------------------------------------------------------------------------------------------------

def GPIO_04_Fall(camera):
    camera.stop_recording()
    print ("Video stop")
    GPIO.output(18, False)
    if bLedOn: camera.led = False
    if debug == True: PrintDebug()

# -------------------------------------------------------------------------------------------------
# convert h264 stream to mp4 and remove not needed files
# MP3Box is used
# -------------------------------------------------------------------------------------------------
def conver_to_mp4(filename):
    
    command_ro_run = "MP4Box -add " + filename + ".h264 " +  filename + ".mp4"
    if debug == True: print (command_ro_run)
    subprocess.call(command_ro_run, shell=True)
    
    command_ro_run = "rm " + filename + ".h264 "
    if debug == True: print (command_ro_run)
    subprocess.call(command_ro_run, shell=True)
   
# -------------------------------------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------------------------------------

with picamera.PiCamera() as camera:

    camera.led = False
    #camera.resolution = (1920, 1080)
    #camera.resolution = (1280, 720)
    camera.exposure_compensation = 2
    camera.exposure_mode = 'auto' # auto sports
    camera.meter_mode = 'matrix'
    camera.image_effect = 'none'
    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2014 PAJAT'
    camera.exif_tags['EXIF.UserComment'] = 'Raspberry Pi - PRICam.py Motion detection'
    
    print ("Capturing mode %s" % CapturingMode)
     
    try:
        while True:
            #camera.wait_recording(1)
            time.sleep(0.01)
            if GPIO.input(4):
                # Check that enough free space is available 
                keepDiskSpaceFree(diskSpaceToReserve)
                # Still mode
                if CapturingMode == "Still":    
                    GPIO_04_Rise(camera, filename)
                # video mode
                else:
                    # Not recording yet
                    if RecordingOn == False:    
                        # Set filename 
                        dt = datetime.now()
                        filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                        # star recording
                        GPIO_04_Rise(camera, filename)
                        # set recording on
                        RecordingOn = True
                    # movement stopped
            else:
                # was recording
                if RecordingOn == True:
                    # stop recording
                    GPIO_04_Fall(camera)
                    # set recording off
                    RecordingOn = False
                    # convert h264 to mp4
                    conver_to_mp4(filename)

    # Cleanup if stopped by using Ctrl-C
    except KeyboardInterrupt:
        print("Cleanup")
        GPIO.cleanup()
