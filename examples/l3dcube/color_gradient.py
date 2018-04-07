#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to smoothly cycle through colors
"""
import time
import spectra

import netl3d
from netl3d.hardware import l3dcube

config = netl3d.parse_config()
debug = config['debug']
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = l3dcube.Controller(ip, port)
controller.set_debug(debug)
controller.handshake()

start = spectra.hsv(0, 1, 1)
finish = spectra.hsv(359, 1, 1)
gradient = [start, finish]

while True:
  my_scale = spectra.scale(gradient)
  frame = l3dcube.CubeFrame()
  for color in my_scale.range(120):
    print('Sending color %s' % color.hexcode)
    frame.fill(color)
    controller.sync(frame)
    time.sleep(0.03)
