"""
 Basic program to decode Raspberry Pi RAW camera images, apply
 debayering and basic colour correction, and show/save results.
 
 Author: Felix Schill
 Some code (reading/array shaping) based on example code from picamera
 http://picamera.readthedocs.org/en/release-1.10/recipes2.html#raw-bayer-data-captures

 Usage:
 python show_raw.py <rawfile.jpg>
 creates a file "out.png" with the decoded image
 
"""

import sys
import numpy as np
import io

import scipy
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.cm as cm

print("opening: ", sys.argv[1])
stream = open(sys.argv[1], 'rb')

width = 2592
height= 1944

data = stream.read()[-6404096:]
assert data[:4] == 'BRCM'
data = data[32768:]
data = np.fromstring(data, dtype=np.uint8)

data = data.reshape((1952, 3264))[:1944, :3240]

data = data.astype(np.uint16) << 2
for byte in range(4):
    data[:, byte::5] |= ((data[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
data = np.delete(data, np.s_[4::5], 1)

# de-bayering
db_rgb = np.zeros((data.shape[0]-1, data.shape[1]-1, 3), dtype=float)

# color channel weights
rw = 1.0
gw = 0.7
bw = 0.9

# color conversion matrix (from raspi_dng/dcraw)
# R        g        b
cvm = np.array(
[[ 1.2782,-0.4059, -0.0379], 
[-0.0478, 0.9066,  0.1413], 
[ 0.1340, 0.1513,  0.5176 ]])

# reorder bayer values (RGGB) into intermediate full-color points (o)
# green is weighted down a bit to give a more neutral color balance	
# 
# G   B   G   B 
#   o   o   o
# R   G   R   G
#   o   o   o
# G   B   G   B

db_rgb[0::2, 0::2, 0] = rw * (data[1::2, 0::2])            # Red
db_rgb[0::2, 0::2, 1] = 0.5* gw * data[0::2, 0::2] \
                      + 0.5* gw * data[1::2, 1::2]          # Green
db_rgb[0::2, 0::2, 2] = bw * data[0::2, 1::2]              # Blue

db_rgb[0::2, 1::2, 0] = rw * data[1::2, 2::2]              # Red
db_rgb[0::2, 1::2, 1] = 0.5* gw * data[0::2, 2::2] \
                      + 0.5* gw * data[1::2, 1::2][:, :-1]  # Green
db_rgb[0::2, 1::2, 2] = bw * data[0::2, 1::2][:, :-1]      # Blue

db_rgb[1::2, 0::2, 0] = rw * data[1::2, 0::2][:-1]         # Red
db_rgb[1::2, 0::2, 1] = 0.5* gw * data[2::2, 0::2] \
                      + 0.5* gw * data[1::2, 1::2][:-1,:]   # Green
db_rgb[1::2, 0::2, 2] = bw * data[2::2, 1::2][:, :]        # Blue

db_rgb[1::2, 1::2, 0] = rw * data[1::2, 2::2][:-1,:]       # Red
db_rgb[1::2, 1::2, 1] = 0.5* gw * data[2::2, 2::2] \
                      + 0.5* gw * data[1::2, 1::2][:-1,:-1] # Green
db_rgb[1::2, 1::2, 2] = bw * data[2::2, 1::2][:, :-1]      # Blue

db_rgb = db_rgb.dot(cvm)

print ("Min/max values:", np.min(db_rgb),np.max(db_rgb))

# appy log to brighten dark tones (the added value reduces effect by flattening the curve)
db_rgb = np.log(db_rgb+80)

#normalize image
db_rgb = (db_rgb-np.min(db_rgb))/(np.max(db_rgb)-np.min(db_rgb))

# show color channels and RGB reconstruction
f, ax = plt.subplots(2,2, sharex=True, sharey=True)
red   = db_rgb[:,:, 0]
green = db_rgb[:,:, 1]
blue  = db_rgb[:,:, 2]

ax[0][0].imshow(-red, interpolation='nearest', cmap = cm.binary)
ax[0][1].imshow(-green, interpolation='nearest', cmap = cm.binary)
ax[1][0].imshow(-blue, interpolation='nearest', cmap = cm.binary)

ax[1][1].imshow(db_rgb, interpolation='nearest', cmap = cm.binary)
f.tight_layout()
plt.show()

# save to file
scipy.misc.toimage(db_rgb).save("out.png")


