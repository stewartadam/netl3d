#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs multiple effects in a simulator, composing them onto a single cube
"""
import netl3d
from netl3d.hardware import l3dcube
from netl3d.simulator import Simulator
import animations

if __name__ == '__main__':
  config = netl3d.parse_config()
  debug = config['debug']
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = l3dcube.Controller(ip, port)
  controller.set_debug(debug)
  controller.handshake()

  sim = Simulator(controller, ticks_per_second=2)
  sim.add_animation(animations.outer_square(l3dcube.CubeFrame()))
  sim.add_animation(animations.heartbeat_cube(l3dcube.CubeFrame()), priority=1)

  sim.run()
