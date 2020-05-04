#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to smoothly cycle through colors
"""
import time
import spectra

import netl3d

config = netl3d.parse_config()
netl3d.configure_logging(config)
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = netl3d.hardware.l3dcube.L3DController(ip, port)
controller.handshake()

start = spectra.hsv(0, 1, 1)
finish = spectra.hsv(359, 1, 1)
gradient = [start, finish]

while True:
  my_scale = spectra.scale(gradient)
  frame = netl3d.hardware.l3dcube.CubeFrame()
  for color in my_scale.range(120):
    print('Sending color %s' % color.hexcode)
    frame.fill(color)
    controller.sync(frame)
    time.sleep(0.03)
