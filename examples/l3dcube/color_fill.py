#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fill the entire cube with the color (r, g, b) specified
"""
import spectra
import sys

import netl3d
from netl3d.hardware import l3dcube

def usage():
  print("Usage: color_fill.py r g b")
  print("\tWhere r, g and b are ints 0 - 255")
  sys.exit(1)

if len(sys.argv[1:]) != 3:
  usage()

try:
  rgb = [float(x)/255 for x in sys.argv[1:]]
except ValueError:
  usage()

config = netl3d.parse_config()
debug = config['debug']
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = l3dcube.Controller(ip, port)
controller.set_debug(debug)
controller.handshake()

color = spectra.rgb(*rgb)
print('Sending color %s' % color.hexcode)
frame = l3dcube.CubeFrame()
frame.fill(color)
controller.sync(frame)
