import logging
import threading
import uuid
from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List, TypeVar

from .transform import FrameTransform
from netl3d.hardware.l3dcube import CubeFrame

PositionType = TypeVar('PositionType')

class FramePublisher:
  """
  Frame publishing event channel. Retains a copy of a published frame and
  notifies any subscribers of published frames.
  """

  def __init__(self) -> None:
    super().__init__()
    self.subscribers: List[Callable] = []
    self.observer_lock = threading.Lock()
    self.logger = logging.getLogger(__name__)
    self.published_frame = CubeFrame()

  def register(self, callback: Callable) -> None:
    with self.observer_lock:
      self.logger.debug(f"registering observer {callback} on {self}")
      self.subscribers.append(callback)

  def unregister(self, callback: Callable) -> None:
    with self.observer_lock:
      self.logger.debug(f"unregistering observer {callback} on {self}")
      self.subscribers.remove(callback)

  def publish(self, frame: CubeFrame) -> None:
    self.logger.debug(f"frame published on {self}")
    self.published_frame = frame.copy()
    with self.observer_lock:
      subscribers_at_time_of_notify = list(self.subscribers)

    for callback in subscribers_at_time_of_notify:
      self.logger.debug(f"-> notifying {callback}")
      callback(self)

  def get_published_frame(self) -> CubeFrame:
    return self.published_frame


class Pipeline(FramePublisher):
  def __init__(self, generator: FramePublisher) -> None:
    super().__init__()
    self.logger = logging.getLogger(__name__)
    self.pipeline: List[Dict[str, object]] = [] # FIXME typing
    self.mutate_lock = threading.Lock()
    self.generator = generator
    self.generator.register(self.run_pipeline)

  def run_pipeline(self, publisher: FramePublisher) -> None:
    self.logger.debug("generator published frame, starting pipeline run")
    with self.mutate_lock:
      frame = publisher.get_published_frame()
      for item in self.pipeline:
        self.logger.debug(f"-> running pipeline item {item['id']}: {item['fg']}")
        frame = item['fg'].apply(frame) # type: ignore
      self._state_linear = list(frame._state_linear)
      self.logger.debug("finished pipeline run, publishing output")

      self.logger.debug(self.generator.subscribers)

      self.publish(frame)

  def add(self, fg: FrameTransform, priority: int = 0) -> str:
    with self.mutate_lock:
      id = str(uuid.uuid4())
      self.pipeline.append({'id': id, 'priority': priority, 'fg': fg})
      self.pipeline = sorted(self.pipeline, key=lambda item: item['priority'], reverse=True)
      return id

  def remove(self, id: str) -> None:
    with self.mutate_lock:
      for item in self.pipeline:
        if item['id'] == id:
          break
      self.pipeline.remove(item)
