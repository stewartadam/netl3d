# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to sequentially iterate through R, B and G color
at full brightness.
"""
import time

import config
import netl3d

controller = netl3d.netl3d(config.DEVICE_IP)

mode = 0
while True:
  led = 0
  while (led + 1 < controller.LED_NUM):
    data = bytearray()
    for i in range(controller.LED_PER_PACKET):
      data.append((mode == 0) * 255)
      data.append((mode == 1) * 255)
      data.append((mode == 2) * 255)
    controller.send_colors(led, data)
    led += controller.LED_PER_PACKET

  print 'Setting LED color to %s' % ('rgb'[mode])
  mode = (mode + 1) % 3

  controller.send_refresh()
  time.sleep(0.5)
