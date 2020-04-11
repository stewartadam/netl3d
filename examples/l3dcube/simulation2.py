#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs multiple effects in a simulator, composing them onto a single cube
"""
import time

import netl3d
from netl3d.hardware import l3dcube
from netl3d.simulator import Simulator, merge_strategy
import animations

if __name__ == '__main__':
  config = netl3d.parse_config()
  debug = config['debug']
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = l3dcube.Controller(ip, port)
  controller.set_debug(debug)
  controller.handshake()

  import threading
  stop = threading.Event()
  sim = Simulator(stop, controller, ticks_per_second=60)
  sim.add_animation(animations.heartbeat_cube, priority=1)

  try:
    sim.start()
    time.sleep(2)
    id1 = sim.add_animation(animations.random_col, priority=4)
    time.sleep(2)
    id2 = sim.add_animation(animations.random_col, priority=4)
    time.sleep(2)
    id3 = sim.add_animation(animations.random_col, priority=4)
    time.sleep(2)
    sim.delete_animation(id1)
    time.sleep(2)
    sim.delete_animation(id2)
    time.sleep(2)
    sim.delete_animation(id3)

    sim.join()
  except KeyboardInterrupt:
    stop.set()
  except:
    stop.set()
    raise
