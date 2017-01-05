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

import config
import netl3d
import shapes

class liveplay:
  def __init__(self, LP, controller, led_state):
    self.LP = LP
    self.controller = controller
    self.led_state = led_state
    self.launchpad_state = {}
    self.shapes = shapes.shapes(self.controller, self.led_state)

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
    self.shapes.wall(index)

  def slice(self, button_id, row, index, pressed):
    self.shapes.slice(index)

  def sheet(self, button_id, row, index, pressed):
    self.shapes.sheet(index)

  def special(self, button_id, row, index, pressed):
    # right side of launchpad
    if row == 0 and pressed:
      # Lights on
      self.led_state.fill(self.controller.get_color(1, 1, 1))
    elif (row == 7 and pressed) or (row == 0 and not pressed):
      # Temporary blackout
      self.led_state.clear()

    # top row of launchpad
    elif row == 12:
      # note: row 12 starts at index=8 for some reason
      increment = 32
      if index == 8 and pressed:
        self.controller.adjust_brightness(increment)
      elif index == 9 and pressed:
        self.controller.adjust_brightness(-increment)

      elif index == 10 and pressed:
        self.controller.adjust_color_mask(1)
      elif index == 11 and pressed:
        self.controller.adjust_color_mask(-1)

  def rebuild(self):
    """
    Rebuilds the L3D state based on pressed buttons only
    """
    self.led_state.clear()
    pressed = True
    for button_id in self.launchpad_state.keys():
      row, index = self.lp2xy(button_id)
      callback = self.lp2callback(button_id)
      callback(button_id, row, index, pressed)
    self.led_state.sync()

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

  controller = netl3d.netl3d(config.DEVICE_IP)
  controller.handshake()
  led_state = netl3d.led_state(controller)

  try:
    liveplay(LP, controller, led_state)
  except KeyboardInterrupt:
    LP.Reset()
    LP.Close()
    raise

