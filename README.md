# raspberry-pi-pircam

## Raspberry Pi motion detection IR Camera with IR lights by TJuTZu

Version 1.7.1

raspberry-pi-pircam-xlight.py is for controlling Raspberry Pi camera module
with PIR motion detector with external IR Lights

Camera shoot video as long movement is detected and take image every 10 minutes.
On application settings is set the reserved free disk space and software takes care it is keps free by removing old recordings.

Still work in progress


### Requirement

* Raspberry Pi
* [Raspberry Pi noir camera] (https://www.raspberrypi.org/products/pi-noir-camera/)
* HC-SR501 Adjust Pyroelectric Infrared IR PIR Motion Sensor Detector
* 48 LED illuminator IR Infrared Night Vision

### Schema

Currently this git doesn't contain the description of electronics needed to run 12V IR light.
Schematic can be found from my [web page] (http://tjutzu.kapsi.fi/wp/raspberry-pi-pircam-2/).

### Note!

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
Currently application saves recorded files by default in /var/www which is created during apache install.

Good file explorer to use with web server is [Encode Explorer] (http://encode-explorer.siineiolekala.net/) it needs PHP be installed.

Install PHP:
```
sudo apt-get install php5 libapache2-mod-php5 -y
```

Install PHP image prosessing:
```
sudo apt-get install php5-gd -y
```

Restart apache
```
sudo service apache2 restart
```
Copy encode-explorer into /var/www/cam directory

Get [Encode Explorer] (http://encode-explorer.siineiolekala.net/) directly from git, remove index.html which is no longer needed

```
wget https://github.com/marekrei/encode-explorer/archive/master.zip
unzip master
sudo cp encode-explorer-master/index.php /var/www/
sudo rm /var/www/index.html
```
modify it according to instructions given on Encode Explorer pages
```
sudo nano /var/www/index.php
```
