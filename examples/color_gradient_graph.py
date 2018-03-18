#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smoothly cycle through colors, always setting the front frame of the L3D cube to
the next color.
"""
import time
import spectra

import config
import netl3d
from netl3d.l3dcube import graph

controller = netl3d.netl3d(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()
g = graph(controller)

start = spectra.hsv(0, 1, 1)
finish = spectra.hsv(359, 1, 1)
gradient = [start, finish]

graph = True

while True:
  my_scale = spectra.scale(gradient)
  for color in my_scale.range(40):
    led = 0
    frame = [[list([int(x*255) for x in color.clamped_rgb])] * 8] * 8
    g.slide(frame)
    print('Sending color %s' % color.hexcode)
    g.sync()
    time.sleep(0.075)
