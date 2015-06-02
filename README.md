# pyraw
RAW image decoding for Raspberry Pi camera in python

Basic program to decode Raspberry Pi RAW camera images, apply
 debayering and basic colour correction, and show/save results.
 
 Author: Felix Schill
 Some code (reading/array shaping) based on example code from picamera
 http://picamera.readthedocs.org/en/release-1.10/recipes2.html#raw-bayer-data-captures

 Usage:
 python show_raw.py <rawfile.jpg>
 creates a file "out.png" with the decoded image

