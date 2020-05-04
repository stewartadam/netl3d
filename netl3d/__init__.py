"""
Common utilities for controlling L3Ds
"""
import logging
import os.path
import yaml

from . import base
from . import effects
from . import hardware
from . import transforms
from . import simulator

def parse_config(config_path: str = "~/.netl3d") -> dict:
  return yaml.safe_load(open(os.path.expanduser(config_path)))


def configure_logging(config: dict) -> None:
  logLevel = getattr(logging, config['logging']['default'].upper())
  logging.basicConfig(level=logLevel)
  for key, value in config['logging'].items():
    if key != 'default':
      logging.getLogger(key).setLevel(getattr(logging, value.upper()))
