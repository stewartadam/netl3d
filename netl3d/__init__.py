# -*- coding: utf-8 -*-
"""
Common utilities for controlling L3Ds
"""
import spectra

class Controller:
  __brightness = 128
  __color_mask = 7
  __debug = False

  def set_debug(self, is_enabled):
    self.__debug = is_enabled

  def get_debug(self):
    return self.__debug

  def debug(self, message):
    if not self.get_debug():
      return
    print(message)

  def get_brightness(self):
    return self.__brightness

  def set_brightness(self, brightness):
    if brightness < 0:
      brightness = 0
    elif brightness > 255:
      brightness = 255
    self.__brightness = brightness

  def adjust_brightness(self, increment):
    self.set_brightness(self.get_brightness() + increment)

  def get_color_mask(self):
    """Returns a (r,g,b) tuple valued with 1 or 0"""
    r = (self.__color_mask >> 2) % 2 == 1
    g = (self.__color_mask >> 1) % 2 == 1
    b = self.__color_mask % 2 == 1
    return (r, g, b)

  def set_color_mask(self, mask):
    self.__color_mask = mask % 8

  def adjust_color_mask(self, increment):
    self.set_color_mask(self.__color_mask + increment)
    if self.__color_mask == 0:
      self.adjust_color_mask(increment)

  def get_color(self, r, g, b, a=None):
    br = self.__brightness if a is None else a
    (r_mask, g_mask, b_mask) = self.get_color_mask()
    return spectra.rgb(r*br*r_mask, g*br*g_mask, b*br*b_mask)
