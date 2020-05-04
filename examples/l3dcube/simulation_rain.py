import spectra
import threading
import time
from enum import Enum
from typing import Any, List, Tuple

import netl3d

if __name__ == '__main__':
  config = netl3d.parse_config()
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = netl3d.hardware.l3dcube.L3DController(ip, port)
  controller.handshake()

  strategy = netl3d.simulator.MergeStrategy.OVERLAY

  stop_signal = threading.Event()
  sim = netl3d.simulator.Simulator(stop_signal, controller)

  def setup_rain() -> None:
    f = netl3d.hardware.l3dcube.CubeFrame()
    fp = netl3d.base.FramePublisher()
    rain = threading.Thread(target=netl3d.effects.rain, args=(f, fp,))
    rain.daemon = True

    pipeline = netl3d.base.Pipeline(fp)
    fade = netl3d.transforms.FadeTransform(3000, start_opacity=0.7, end_opacity=0.2)
    id = pipeline.add(fade)
    threading.Timer(6.0, pipeline.remove, args=(id,)).start()

    rain.start()
    sim.add_publisher(pipeline)

  sim.start()

  for i in range(6):
    setup_rain()

  try:
    sim.join()
  except KeyboardInterrupt:
    stop_signal.set()