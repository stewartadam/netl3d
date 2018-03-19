#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets all LEDs in the L3D cube to sequentially iterate through R, B and G color.
"""
import spectra
import sys
import time

import config
import netl3d
from netl3d.hardware import l3dcube

controller = l3dcube.Controller(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()

(x, y, z) = [int(i) for i in sys.argv[1:4]]

frame = l3dcube.CubeFrame()
frame.set_brightness_mask(.5)
frame.set_led((x, y ,z), spectra.rgb(1, 1, 1))
controller.sync(frame)
