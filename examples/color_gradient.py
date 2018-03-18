#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to smoothly cycle through colors
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
  for color in my_scale.range(120):
    led = 0
    while (led + 1 < controller.LED_NUM):
      data = bytearray()
      for i in range(controller.LED_PER_PACKET):
        data.append(int(color.clamped_rgb[0] * 255))
        data.append(int(color.clamped_rgb[1] * 255))
        data.append(int(color.clamped_rgb[2] * 255))
      controller.send_colors(led, data)
      led += controller.LED_PER_PACKET

    print('Sending color %s' % color.hexcode)
    controller.send_refresh()
    time.sleep(0.03)
