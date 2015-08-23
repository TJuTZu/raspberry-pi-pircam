# raspberry-pi-pircam
===================

## Raspberry Pi motion detection IR Camera with IR lights by TJuTZu
----------------------------------------------------------------

Version 1.7.1

raspberry-pi-pircam-xlight.py is for controlling Raspberry Pi camera module
with PIR motion detector with external IR Lights

Still work in progress


### Requirement

* Raspberry Pi
* [Raspberry Pi noir camera] (https://www.raspberrypi.org/products/pi-noir-camera/)
* HC-SR501 Adjust Pyroelectric Infrared IR PIR Motion Sensor Detector
* 48 LED illuminator IR Infrared Night Vision

### Note!

Currently this git doesn't contain the description of electronics needed to run 12V IR light.
Recordings are stored in /var/www on default configuration, change it if web server is not used

### Installation

Instructions and how to install Depian on SD card can be found from [raspberrypi.org] (https://www.raspberrypi.org/downloads/) pages

It is good to update Raspberry Pi before installing additional componets
```
sudo apt-get update
sudo apt-get upgrade
```
Application uses MP4Box to convert recorded .h264 files to .mp4

Install:

```
sudo apt-get install gpac
```
To be able to see recorded files trough web apache is needed Install apache:

```
sudo apt-get install apache2 -y
```
Currently application saves recorded files by default in /var/www/cam folder which need to be created.

```
mkdir /var/www/cam
```
Good file explorer to use with web server is [Encode Explorer] (http://encode-explorer.siineiolekala.net/) it needs PHP be installed.

Install PHP:
```
sudo apt-get install php5 libapache2-mod-php5 -y
```

Restart apache
```
sudo service apache2 restart
```
Copy encode-explorer into /var/www/cam directory
