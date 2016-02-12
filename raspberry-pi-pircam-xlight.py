# -------------------------------------------------------------------------------------------------
#
# raspberry-pi-pircam.py ver 1.7.1
#
# Raspberry Pi motion detection IR Camera with extra IR Led
# by TJuTZu
#
# Thanks to (I really can't name all) the people whose code I have used as a base
#
# picamera documentation can be found http://picamera.readthedocs.org/
#
# MP4Box is used for video conversion to install
#  sudo apt-get update
#  sudo apt-get install gpac
#
# -------------------------------------------------------------------------------------------------
# 1.7
# - Some reorganizing the code
# - Configuration moved to ini file
# 1.7.1
# - Edded event handling to detect when sensor is triggered, used to detect how PIR works
# - Noted that PIR was set to single trigger mode and that was causing all the recordings
#   to be exatly same length
# 1.7.2
# - Also picture is taken when video recording starts
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
# For debugging purposes
# -------------------------------------------------------------------------------------------------
#import warnings
#warnings.filterwarnings('error', category=DeprecationWarning)

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
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()
GPIO.setwarnings(False)

GPIO.setup(4, GPIO.IN)
#GPIO.setup(18, GPIO.OUT)
#GPIO.output(18, False)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, False)

# -------------------------------------------------------------------------------------------------
# inifile handling
# -------------------------------------------------------------------------------------------------
from ConfigParser import SafeConfigParser
inifile = SafeConfigParser()

# -------------------------------------------------------------------------------------------------
# Read value from inifile
# -------------------------------------------------------------------------------------------------
def get_ini(self, section, value, default):
  if self.has_option(section, value) == False:
    return default
  else:
    return self.get(section, value)

# -------------------------------------------------------------------------------------------------
# Add new method to SafeConfigParser 
# -------------------------------------------------------------------------------------------------
setattr(SafeConfigParser, 'get_ini', get_ini)

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
    #text = "%04d.%02d.%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) 
    text = "-%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) 
    return text 

# -------------------------------------------------------------------------------------------------
# IR Light on/off
# -------------------------------------------------------------------------------------------------
def IRLight(onoff):
    # External IR light
    if bIrLight: GPIO.output(24, onoff)

# -------------------------------------------------------------------------------------------------
# Turn extra IR on
# Start video recording
# -------------------------------------------------------------------------------------------------
def StartVideoRecording(camera, target_filename):
        
    logging.debug ("StartVideoRecording")
    
    # Turn IR Led on
    IRLight(True)

    if bLedOn: camera.led = True

    # Set file extension
    target_filename = target_filename + ".h264"

    logging.debug ("Start recording %s" % target_filename)
    camera.start_recording(target_filename, format='h264')
    logging.debug ("Started recording")
    
    # take picture
    if bVidPic:
      target_filename = target_filename + ".jpg"
      logging.debug ("Taking Video Picture %s" % target_filename)
      camera.capture(target_filename, use_video_port=True)
       
    if bLedOn: camera.led = False

     
# -------------------------------------------------------------------------------------------------
# Stop video recording
# Turn extra IR off
# -------------------------------------------------------------------------------------------------

def StopVideoRecording(camera):
    logging.debug ("StopVideoRecording")
    camera.stop_recording()
    IRLight(False)
    if bLedOn: camera.led = False

# -------------------------------------------------------------------------------------------------
# convert h264 stream to mp4 and remove not needed files
# HOX!! MP3Box need to available!
# -------------------------------------------------------------------------------------------------
def conver_to_mp4(target_filename):
    
    command_ro_run = "MP4Box -add " + target_filename + ".h264 " +  target_filename + ".mp4"
    if debug == True: logging.debug (command_ro_run)
    subprocess.call(command_ro_run, shell=True)
    
    command_ro_run = "remove: " + target_filename + ".h264 "
    if debug == True: logging.debug (command_ro_run)
    os.remove(target_filename + ".h264")
   
# -------------------------------------------------------------------------------------------------
# Event for testing PIR
# -------------------------------------------------------------------------------------------------

def GPIO_04_Event(channel):
    if GPIO.input(4):
        logging.debug ("Event: RISING!")
    else:
        logging.debug ("Event: FALLING!")


# -------------------------------------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------------------------------------

print os.path.dirname(os.path.realpath(__file__))

# Read configuration file
inifile.read(os.path.dirname(os.path.realpath(__file__)) + "/raspberry-pi-pircam-xlight.ini")
# Debug
readok = "True" == inifile.get_ini("Debug", "readok", False)
debug = "True" == inifile.get_ini("Debug", "debug", False)

# Filesystem
filepath = inifile.get_ini("Filesystem", "filepath", "/var/www")
filenamePrefix = inifile.get_ini("Filesystem", "filenamePrefix", "PIR")
diskSpaceToReserve = int(inifile.get_ini("Filesystem", "diskSpaceToReserve", 1048576)) # 1024 * 1024 * 1024 - Keep 1024 mb free on disk

# Light
# True / False - Ir light in use
bIrLight = "True" == inifile.get_ini("Light", "IrLight", False)  

# Camera
# True / False - Camera led
bLedOn = "True" == inifile.get_ini("Camera", "LedOn", False)
bVidPic = "True" == inifile.get_ini("Camera", "VideoPicture", False)
# auto,night,nightpreview,backlight,spotlight,sports,snow,beach,verylong,fixedfps,antishake,fireworks
camera_exposure_mode = inifile.get_ini("Camera", "camera_exposure_mode",'auto')
camera_exposure_compensation = int(inifile.get_ini("Camera", "camera_exposure_compensation", "2"))
camera_meter_mode = inifile.get_ini("Camera", "camera_meter_mode",'matrix')
camera_hflip = "True" == inifile.get_ini("Camera", "camera_hflip", False) # Flip camera image horisontally
camera_vflip = "True" == inifile.get_ini("Camera", "camera_vflip", False) # Flip camera image vertically
camera_image_effect = inifile.get_ini("Camera", "camera_image_effect",'none')
camera_exif_tags_IFD0_Copyright = inifile.get_ini("Camera", "camera_exif_tags_IFD0_Copyright",'Copyright (c) 2015 TJuTZu')
camera_exif_tags_EXIF_UserComment = inifile.get_ini("Camera", "camera_exif_tags_EXIF_UserComment",'Raspberry Pi - PRICam.py Motion detection')
#camera_resolution_w = ''
#camera_resolution_h = ''

GPIO.add_event_detect(4, GPIO.BOTH, callback=GPIO_04_Event)


# -------------------------------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------------------------------

# for debug
logfile = filepath + "/" + filenamePrefix + DateText() + ".log"

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=logfile,level=logging.DEBUG)
logging.debug ("Logs to: %s" % logfile)

logging.debug ("Inifile: " + os.path.dirname(os.path.realpath(__file__)) + "/raspberry-pi-pircam-xlight.ini")
logging.debug ("readok: %s" % (readok == True))
logging.debug ("debug: %s" % debug)
logging.debug ("filepath: %s" % filepath)
logging.debug ("filenamePrefix: %s" % filenamePrefix)
logging.debug ("diskSpaceToReserve: %d bytes / %d kb / %d Mb / %d Gb" % (diskSpaceToReserve, diskSpaceToReserve/1024, diskSpaceToReserve/1024/1024, diskSpaceToReserve/1024/1024/1024)) 
logging.debug ("bIrLight: %s" % bIrLight)
logging.debug ("bLedOn: %s" % bLedOn)    
logging.debug ("bVidPic: %s" % bVidPic)    
logging.debug ("camera_exposure_mode: %s" % camera_exposure_mode)
logging.debug ("camera_exposure_compensation: %d" % int(camera_exposure_compensation))
logging.debug ("camera_meter_mode: %s" % camera_meter_mode)
logging.debug ("camera_hflip: %s" % camera_hflip)
logging.debug ("camera_vflip: %s" % camera_vflip)
logging.debug ("camera_image_effect: %s" % camera_image_effect)
logging.debug ("camera_exif_tags_IFD0_Copyright: %s" % camera_exif_tags_IFD0_Copyright)
logging.debug ("camera_exif_tags_EXIF_UserComment %s" % camera_exif_tags_EXIF_UserComment)

# -------------------------------------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------------------------------------

with picamera.PiCamera() as camera:

    # Camera is not currently recording
    RecordingOn   = False

    camera.led = False
    camera.exposure_compensation = camera_exposure_compensation
    camera.exposure_mode = camera_exposure_mode
    camera.meter_mode = camera_meter_mode
    camera.hflip = camera_hflip
    camera.vflip = camera_vflip
    camera.image_effect = camera_image_effect
    camera.exif_tags['IFD0.Copyright'] = camera_exif_tags_IFD0_Copyright
    camera.exif_tags['EXIF.UserComment'] = camera_exif_tags_EXIF_UserComment
    
    logging.debug ("Capturing mode video")
    
    lastpicturetaken = datetime.now() 
     
    try:
        while True:
            # Wait 1/10th of second
            time.sleep(0.1)
            # Get time
            dt = datetime.now()
            # Check if movement is detected
            if GPIO.input(4):
                logging.debug ("Movement detected!")
                # Check that enough free space is available 
                keepDiskSpaceFree(diskSpaceToReserve)
                # Not recording yet
                if RecordingOn == False:    
                    logging.debug ("Not Recording")
                    # Set filename 
                    filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                    # star recording
                    StartVideoRecording(camera, filename)
                    # set recording on
                    RecordingOn = True
                else:
                    annotate_text = "%04d.%02d.%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                    camera.annotate_text = annotate_text  
                    logging.debug ("Recording: %s" % annotate_text)
                    camera.wait_recording(1)
            # movement stopped
            else:
                # was recording
                if RecordingOn == True:
                    logging.debug ("Movement stopped while recording")
                    # stop recording
                    logging.debug ("Call: StopVideoRecording")
                    StopVideoRecording(camera)
                    # set recording off
                    RecordingOn = False
                    # convert h264 to mp4
                    logging.debug ("Call: conver_to_mp4")
                    conver_to_mp4(filename)
                else:
                    # take picture every 10 minutes (when minutes are devided to 10)
                    if (dt.minute % 10) == 0 and dt.second == 0:
                        # Set annotate text
                        annotate_text = "%04d.%02d.%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                        camera.annotate_text = annotate_text
                        filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) + ".jpg"
                        logging.debug ("Capture %s" % filename)
                        # IR Ligth on
                        IRLight(True)
                        # take picture
                        camera.capture(filename)
                        # IR Ligth off
                        IRLight(False)
                        time.sleep(1)

    # Cleanup if stopped by using Ctrl-C
    except KeyboardInterrupt:
        if RecordingOn == True:
            StopVideoRecording(camera)
            conver_to_mp4(filename)
        logging.debug("Cleanup")
        GPIO.cleanup()

    except Exception as e:
      logging.debug ("Error %s" % str(e))