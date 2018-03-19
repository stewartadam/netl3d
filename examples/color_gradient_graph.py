#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smoothly cycle through colors, always setting the front frame of the L3D cube to
the next color.
"""
import time
import spectra

import config
from netl3d.hardware import l3dcube

controller = l3dcube.GraphController(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()

start = spectra.hsv(0, 1, 1)
finish = spectra.hsv(359, 1, 1)
gradient = [start, finish]

while True:
  my_scale = spectra.scale(gradient)
  for color in my_scale.range(40):
    print('Sending color %s' % color.hexcode)

    frame = l3dcube.GraphFrame()
    frame.fill(color)
    controller.sync(frame)
    time.sleep(0.075)
