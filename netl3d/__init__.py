# -*- coding: utf-8 -*-
"""
Common utilities for controlling L3Ds
"""
import os.path
import spectra
import yaml

def parse_config(config_path="~/.netl3d"):
  return yaml.safe_load(open(os.path.expanduser(config_path)))

class Controller:
  __debug = False

  def set_debug(self, is_enabled):
    self.__debug = is_enabled

  def get_debug(self):
    return self.__debug

  def debug(self, message):
    if not self.get_debug():
      return
    print(message)
