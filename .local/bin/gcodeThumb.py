#!/usr/bin/env python3
##
## gcodeThumbnails
##
## Copyright 2023 Henry Kroll <nospam@thenerdshow.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
## MA 02110-1301, USA.

from base64 import b64decode
from io import BytesIO
from PIL import Image, ImageDraw
import sys, time, re, os

# defaults
size = default_size = (128, 128)
# line color, for drawn thumbnails
line_color = (0,64,100)

def getSize(txt):
    # get size tuple (X,Y) from text like "128" or "128x128"
    size = txt.split("x")[:2]
    size[0] = int(size[0])
    if len(size) < 2:
        size.append(size[0])
    else:
        size[1] = int(size[1])
    if size[0] < 16 or size[1] < 16:
        size = default_size
    return tuple(size)

# process arguments
args = sys.argv
if len(args) < 2:
    # print help message
    print("usage: gcodeThumb.py input_gcode [output_png] [NxN (image size)]")
    exit(1)

input_gcode = args[1]
output_png = os.path.splitext(input_gcode)[0]+ '.png'
if len(args) > 2:
    output_png = args[2]
if len(args) > 3:
    size = getSize(args[3])

img_width, img_height = size

# Configure slicer to put thumbnails in header comments.
# They look better. And this function can extract them.
def getHeaderThumbs(gcode):
    thumbnails = []
    # get one thumbnail from Base64 gcode comment
    def getThumb(gcode):
        imageBase64 = ""
        # read image data
        for line in gcode:
            text = line.split()
            # break on unexpected input
            if len(text) < 2 or text[0] != ";" or text[1] == 'thumbnail':
                break
            imageBase64 += text[1]
        imageBase64 += "=="
        return imageBase64

    # get more thumbnails from header
    for line in gcode:
        # stop at start of gcode (end of header)
        if line[0] >= 'G':
            break

        # get a thumbnail, if present
        text = line.split()
        if len(text) > 2 and text[1] == 'thumbnail' and text[2] == 'begin':
            # add to thumbnail collection
            thumbnails.append(getThumb(gcode))

    # get largest thumbnail
    ll = 0; lt = ""
    for thumb in thumbnails:
        l = len(thumb)
        if l > ll:
            ll = l; lt = thumb

    return Image.open(BytesIO(b64decode(lt))).resize(size) if lt else False

# Attempt to draw a thumbnail manually
def drawFromGcode(gcode, size):
    im = Image.new("RGBA", size, 7)
    draw=[]
    layers=[]
    # initialize scaling factors
    img_width, img_height = size
    AX, AY, AZ = (1000, 1000, 1000)
    BX, BY, BZ = (-1000, -1000, -1000)
    # we all need to start somewhere
    X, Y, Z = (0, 0, 0)
    oldZ = Z
    for block in gcode:
        Z2 = (img_height-Z)*.75
        words = block.split(" ")
        if len(words) > 1 and words[0] in ["G1", "G2", "G3"]:

            # draw any changes in X or Y
            for field in words:
                if len(field) > 3:
                    if field[1] > '9' or field[1] < '-':
                        continue
                    digits = re.sub(r"[^0-9-.]+", "", field[1:])
                    f=field[0];
                    if f=="F":
                        X = 0
                        layers.append(draw)
                        draw = []
                        break
                    try:
                        val=float(digits)
                    except:
                        pass
                    X=val if f=='X' else X
                    Y=val if f=='Y' else Y
                    if f=='Z':
                        Z=val
                        if (Z-oldZ) >= 0.2:
                            layers.append(draw)
                            draw = []
                            oldZ = Z
            
            # if we have something to draw, then draw it to scale
            if X:
                ZY = Y - Z2
                draw.append((X, ZY))
                AX = X if X<AX else AX
                AY = ZY if ZY<AY else AY
                BX = X if X>BX else BX
                BY = ZY if ZY>BY else BY
        elif words[0] == "G27": # park toolhead
            break

    layers.append(draw)
    # scale to view
    MX, MY = (BX-AX, BY-AY)
    SX, SY = (img_width/MX, img_height/MY)
    scaled = []

    # draw the image
    d = ImageDraw.Draw(im)
    R,G,B = line_color
    ll = len(layers)
    if ll > 5:
        layers = layers[3:-2]
    if ll < 25.0:
        ll = 25.0
    s = 128.0 / ll
    for draw in layers:
        for point in draw:
            (X, Y) = point
            X = (X - AX) * SX
            Y = (Y - AY) * SY
            scaled.append((X, img_height - Y))
        d.point(scaled)
        d.line(scaled, fill=(int(R),int(G),int(B)), width=2)
        R+=s;B+=s;G+=s
        # reverse shading direction
        if R>200 or B>200 or G>200 or R<0 or B<0 or G<0:
            s = -s
        scaled = []
    return im

gcode = open(input_gcode, 'r')
im = getHeaderThumbs(gcode)
im = im if im else drawFromGcode(gcode, size)
im.save(output_png, 'png')
