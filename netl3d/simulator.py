import logging
import spectra
import threading
import time
import uuid
from enum import Enum
from typing import Dict, List

import netl3d


class MergeStrategy(Enum):
  OVERLAY = 1
  DIFFERNECE = 2
  ADD = 3
  SUBTRACT = 4
  EXCLUSIVE = 5
  AVERAGE = 6

class Simulator(threading.Thread):
  def __init__(self, stop_signal: threading.Event, controller: netl3d.base.Controller, ticks_per_second: int = 30) -> None:
    threading.Thread.__init__(self)
    self.logger = logging.getLogger(__name__)
    self.mutate_lock = threading.Lock()
    self.stop_signal = stop_signal
    self.controller = controller
    self.ticks_per_second = ticks_per_second
    self.tick_num = 0
    # FIXME: publishers should just be another pipeline
    # to do that we'll need to fix pipeline to merge frames, not a sequential apply()
    self.publishers: List[Dict[str, object]] = [] # FIXME typing

  def add_publisher(self, fp: netl3d.base.FramePublisher, priority: int = 0, merge_strategy: MergeStrategy = MergeStrategy.OVERLAY) -> str:
    with self.mutate_lock:
      self.logger.debug(f"adding publisher {fp} to simulation")
      id = str(uuid.uuid4())
      self.publishers.append({'id': id, 'priority': priority, 'fp': fp, 'merge_strategy': merge_strategy})
      self.publishers = sorted(self.publishers, key=lambda item: item['priority'], reverse=True)
      return id

  def remove_publisher(self, id: str) -> None:
    with self.mutate_lock:
      for item in self.publishers:
        if item['id'] == id:
          break
      self.logger.debug(f"removing publisher {item['fg']} from simulation")
      self.publishers.remove(item)

  def run(self) -> None:
    self.logger.debug("starting simulation")
    while not self.stop_signal.is_set():
      frame = self.merge()
      self.controller.sync(frame)
      time.sleep(1.0 / self.ticks_per_second)
    self.logger.debug("stopping simulation")

  def merge(self) -> netl3d.hardware.l3dcube.CubeFrame:
    self.logger.debug("starting frame merge")
    master_frame = netl3d.hardware.l3dcube.CubeFrame()
    for publisher in self.publishers:
      self.logger.debug(f"-> merging frame from publisher {publisher['fp']} with {publisher['merge_strategy']}")
      frame = publisher['fp'].get_published_frame() # type: ignore
      zero = master_frame.get_color(0, 0, 0)
      if publisher['merge_strategy'] == MergeStrategy.OVERLAY:
        for i in range(len(frame._state_linear)):
          if master_frame._state_linear[i].clamped_rgb == zero.clamped_rgb:
            master_frame._state_linear[i] = frame._state_linear[i]
      elif publisher['merge_strategy'] == MergeStrategy.EXCLUSIVE:
        master_frame._state_linear = frame._state_linear
        break
      elif publisher['merge_strategy'] == MergeStrategy.AVERAGE:
        for i in frame._state_linear:
          c1 = master_frame._state_linear[i].to("hsv")
          c2 = frame._state_linear[i].to("hsv")
          master_frame._state_linear[i] = c1.blend(c2).clamped_rgb*255
      else:
        raise ValueError(f"Invalid merge strategy: {publisher['merge_strategy']}")
    return master_frame
