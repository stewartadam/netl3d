#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads input from the launchpad to controls lighting patterns on the L3D cube.

Eventual goal is to support a 'live play' mode as well as scripted animations
via a plugin system with a configurable button mapping.

Currently, supported buttons and their corresponding actions are:
- Up/Down: Control brightness (1/8 increments)
- Left/Right: Cycle colors (8-bit RGB color mask)
- Top right: Force-on all LEDs (takes precedence over others)
- Bottom right: Force-off all LEDs (takes precedence over others)
- Row 1: Produce a 8x8 pixel wall (zy-plane), offset on the L3D cube equal to the button index
- Row 2: Produce a 8x8 pixel slice (xz-plane), offset on the L3D cube equal to the button index
- row 3: Produce a 8x8 pixel sheet (xy-plane), offset on the L3D cube equal to the button index
"""
import pygame
import launchpad_py

import netl3d
from netl3d.hardware import l3dcube

class liveplay:
  def __init__(self, LP, controller):
    self.LP = LP
    self.controller = controller
    self.launchpad_state = {}
    self.led_state = l3dcube.CubeFrame()

    self.LP.Reset()

    while 1:
      pygame.time.wait(5)

      but = self.LP.ButtonStateRaw()
      if but != []:
        button_id = but[0]
        pressed = but[1]
        row, index = self.lp2xy(button_id)
        print('%s: bid=%d, row=%d, index=%d, pressed=%s' % (but, button_id, row, index, pressed))

        if pressed:
          self.launchpad_state[button_id] = True
          self.LP.LedCtrlRaw(button_id, 0, 3)
        else:
          self.launchpad_state.pop(button_id)
          self.LP.LedCtrlRaw(button_id, 0, 0)
        self.rebuild()

    self.LP.Reset() # turn all LEDs off
    self.LP.Close() # close the Launchpad

  def null(self, button_id, row, index, pressed):
    pass

  def wall(self, button_id, row, index, pressed):
    return l3dcube.shapes.wall(index, frame=self.led_state)

  def slice(self, button_id, row, index, pressed):
    return l3dcube.shapes.slice(index, frame=self.led_state)

  def sheet(self, button_id, row, index, pressed):
    return l3dcube.shapes.sheet(index, frame=self.led_state)

  def special(self, button_id, row, index, pressed):
    # right side of launchpad
    if row == 0 and pressed:
      # Lights on
      self.led_state.fill(self.led_state.get_color(1, 1, 1))
    elif (row == 7 and pressed) or (row == 0 and not pressed):
      # Temporary blackout
      self.led_state.clear()

    # top row of launchpad
    elif row == 12:
      # note: row 12 starts at index=8 for some reason
      increment = 1.0/8
      if index == 8 and pressed:
        self.led_state.adjust_brightness_mask(increment)
      elif index == 9 and pressed:
        self.led_state.adjust_brightness_mask(-increment)

      elif index == 10 and pressed:
        self.led_state.adjust_color_mask(1)
      elif index == 11 and pressed:
        self.led_state.adjust_color_mask(-1)

  def rebuild(self):
    """
    Rebuilds the L3D state based on pressed buttons only
    """
    self.led_state.clear()
    pressed = True
    for button_id in self.launchpad_state.keys():
      row, index = self.lp2xy(button_id)
      callback = self.lp2callback(button_id)
      print ("%d -> %d,%d = %s" % (button_id, row, index, callback))
      callback(button_id, row, index, pressed)
    self.controller.sync(self.led_state)

  def lp2callback(self, button_id):
    row, index = self.lp2xy(button_id)
    callback = 'null'
    if index > 7:
      callback = 'special'
    elif row == 0:
      callback = 'wall'
    elif row == 1:
      callback = 'slice'
    elif row == 2:
      callback = 'sheet'
    return getattr(self, callback)

  def lp2xy(self, button_id):
    # button ID is 16*row + index
    row = button_id // 16
    index = button_id % 16
    return (row, index)

if __name__ == '__main__':
  LP = launchpad_py.Launchpad()
  LP.Open()

  config = netl3d.parse_config()
  debug = config['debug']
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = l3dcube.Controller(ip, port)
  controller.set_debug(debug)
  controller.handshake()

  try:
    liveplay(LP, controller)
  except:
    LP.Reset()
    LP.Close()
    raise

