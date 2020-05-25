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

color_count = 8
start = spectra.hsv(0, 1, 1)
finish = spectra.hsv(360/color_count*(color_count-1), 1, 1)
gradient = [start, finish]

while True:
  my_scale = spectra.scale(gradient)
  frame = netl3d.hardware.l3dcube.CubeFrame()
  for color in my_scale.range(color_count):
    brightness_range = list(range(30, 256, 10))
    brightness_range.reverse()
    brightness_range = list(range(30, 256, 10)) + brightness_range
    for brightness in brightness_range:
      br_factor = brightness/255.0
      (r,g,b) = color.clamped_rgb
      brightened_color = spectra.rgb(r*br_factor, g*br_factor, b*br_factor)
      frame.fill(brightened_color)
      print(f'Sending color {color.hexcode}@{brightness}->{brightened_color.hexcode}')
      controller.sync(frame)
      time.sleep(0.03) # roughly 30fps
