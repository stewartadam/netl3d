import abc
from typing import Type

from .frame import Frame


class Controller(abc.ABC):
  @abc.abstractmethod
  def sync(self, frame: Frame) -> None:
    raise NotImplementedError