from __future__ import annotations # https://stackoverflow.com/a/33533514

import abc
from typing import Callable, Generic, Tuple, TypeVar

import spectra


PositionType = TypeVar('PositionType')

class Frame(abc.ABC, Generic[PositionType]):
  """
  Interface and common functions for hardware-specific LED frames. Maintains
  an in-memory LED state that can be synchronized to a device.
  """
  _brightness_mask = 0.8
  _color_mask = 7

  def __init__(self) -> None:
    self.clear()

  def _apply_masks(self, color: spectra.rgb) -> spectra.rgb:
    """Returns the LED state at the given pos, applying any masks"""
    br_mask = self._brightness_mask or 1.0
    (r, g, b) = color.clamped_rgb
    (r_mask, g_mask, b_mask) = self.get_color_mask()
    return spectra.rgb(r*br_mask*r_mask, g*br_mask*g_mask, b*br_mask*b_mask)

  def get_led(self, pos: PositionType) -> spectra.rgb:
    """Returns the LED state at the given pos, applying any masks"""
    return self._apply_masks(self.get_led_raw(pos))

  @abc.abstractmethod
  def get_led_raw(self, pos: PositionType) -> spectra.rgb:
    """Returns the LED state at the given pos"""
    raise NotImplementedError

  @abc.abstractmethod
  def set_led(self, pos: PositionType, state: spectra.rgb) -> None:
    """Sets the LED state at the given pos"""
    raise NotImplementedError

  @abc.abstractmethod
  def copy(self) -> Frame[PositionType]:
    """Returns a deep copy of the frame"""
    raise NotImplementedError

  @abc.abstractmethod
  def fill(self, color: spectra.rgb) -> None:
    raise NotImplementedError

  def clear(self) -> None:
    self.fill(spectra.rgb(0,0,0).to('hsv'))

  def get_brightness_mask(self) -> float:
    return self._brightness_mask

  def set_brightness_mask(self, brightness_mask: float) -> None:
    if brightness_mask < 0:
      brightness_mask = 0
    elif brightness_mask > 1:
      brightness_mask = 1
    self._brightness_mask = brightness_mask

  def adjust_brightness_mask(self, increment: int) -> None:
    self.set_brightness_mask(self.get_brightness_mask() + increment)

  def get_color_mask(self) -> Tuple[int, int, int]:
    """Returns a (r,g,b) tuple valued with 1 or 0"""
    r = (self._color_mask >> 2) % 2 == 1
    g = (self._color_mask >> 1) % 2 == 1
    b = self._color_mask % 2 == 1
    return (r, g, b)

  def set_color_mask(self, mask: int) -> None:
    self._color_mask = mask % 8

  def adjust_color_mask(self, increment: int) -> None:
    self.set_color_mask(self._color_mask + increment)
    if self._color_mask == 0:
      self.adjust_color_mask(increment)

  def get_color(self, r: int, g: int, b: int, a: int=None) -> spectra.rgb:
    br = self._brightness_mask if a is None else a
    (r_mask, g_mask, b_mask) = self.get_color_mask()
    return spectra.rgb(r*br*r_mask, g*br*g_mask, b*br*b_mask)