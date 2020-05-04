#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Identifies a LED position in the cube by setting a specific (x, y ,z) to white
"""
import spectra
import sys
import time

import netl3d
from netl3d.hardware import l3dcube

def usage():
  print("Usage: test_3d_pos.py x y z")
  print("\tWhere x, y and z are ints 0 - 7")
  sys.exit(1)

if len(sys.argv[1:]) != 3:
  usage()

try:
  (x, y, z) = [int(i) for i in sys.argv[1:4]]
except ValueError:
  usage()

config = netl3d.parse_config()
netl3d.configure_logging(config)
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = l3dcube.L3DController(ip, port)
controller.handshake()

frame = l3dcube.CubeFrame()
frame.set_brightness_mask(.5)
frame.set_led((x, y ,z), spectra.rgb(1, 1, 1))
controller.sync(frame)
