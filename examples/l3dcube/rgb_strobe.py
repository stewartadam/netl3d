#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to sequentially iterate through R, B and G color
33 times/second (epilepsy warning)
"""
import spectra
import time

import netl3d
from netl3d.hardware import l3dcube

config = netl3d.parse_config()
netl3d.configure_logging(config)
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = l3dcube.L3DController(ip, port)
controller.handshake()

mode = 0
while True:
  print('Setting LED color to %s' % ('rgb'[mode]))

  frame = l3dcube.CubeFrame()
  frame.set_brightness_mask(.5)
  frame.fill(spectra.rgb((mode == 0), (mode == 1), (mode == 2)))
  controller.sync(frame)

  mode = (mode + 1) % 3
  time.sleep(0.05) # ~15fps per measurement
