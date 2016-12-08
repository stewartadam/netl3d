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
import launchpad

import config
import netl3d

class animations:
  def __init__(self, LP, controller):
    self.LP = LP
    self.controller = controller

    self.LP.Reset()

    launchpad_state = {}
    led_state = []
    for i in range(controller.LED_NUM):
      led_state.append([0, 0, 0])

    while 1:
      pygame.time.wait(5)

      but = self.LP.ButtonStateRaw()
      if but != []:
        button_id = but[0]
        pressed = but[1]
        row, index = self.lp2xy(button_id)
        print '%s: bid=%d, row=%d, index=%d, pressed=%s' % (but, button_id, row, index, pressed)

        if pressed:
          # the rebuild will take care of ensuring pressed buttons have their
          # lighting effects applied
          launchpad_state[button_id] = True
          self.LP.LedCtrlRaw(button_id, 0, 3)
        else:
          # run the appropriate callback to unset LEDs for the effect, then
          # rebuild L3D state to ensure that if other buttons are still pressed
          # while this button was released, the unset operation doesn't
          # deactivate LEDs that should still be on due to other button presses
          launchpad_state.pop(button_id)
          callback = self.lp2callback(button_id)
          callback(led_state, button_id, row, index, pressed)
          self.LP.LedCtrlRaw(button_id, 0, 0)
        self.rebuild(launchpad_state, led_state)

    self.LP.Reset() # turn all LEDs off
    self.LP.Close() # close the Launchpad

  # L3D indexes start far back, bottom right and count upward to the right,
  # then forward
  def null(self, led_state, button_id, row, index, pressed):
    pass

  def wall(self, led_state, button_id, row, index, pressed):
    for i in range (index*64, (index+1)*64):
      led_state[i] = self.controller.get_color(pressed, pressed, pressed)

  def slice(self, led_state, button_id, row, index, pressed):
    for i in range(8):
      for j in range(8):
        led_state[index*8 + i*64+j] = self.controller.get_color(pressed, pressed, pressed)

  def sheet(self, led_state, button_id, row, index, pressed):
    for i in range(self.controller.LED_NUM / 8):
      led_state[index + i*8] = self.controller.get_color(pressed, pressed, pressed)

  def special(self, led_state, button_id, row, index, pressed):
    # right side of launchpad
    if row == 0 and pressed:
      # Lights on
      for i in range(len(led_state)):
        led_state[i] = self.controller.get_color(1, 1, 1)
    elif (row == 7 and pressed) or (row == 0 and not pressed):
      # Temporary blackout
      for i in range(len(led_state)):
        led_state[i] = [0, 0, 0]

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

  def rebuild(self, launchpad_state, led_state):
    """
    Rebuilds the L3D state based on pressed buttons only
    """
    pressed = True
    for button_id in launchpad_state.keys():
      row, index = self.lp2xy(button_id)
      callback = self.lp2callback(button_id)
      callback(led_state, button_id, row, index, pressed)

    start_l3d_offset = 0
    while (start_l3d_offset + 1 < self.controller.LED_NUM):
      data = bytearray()
      for i in range(self.controller.LED_PER_PACKET):
        l3d_offset = start_l3d_offset + i
        data.append(led_state[l3d_offset][0])
        data.append(led_state[l3d_offset][1])
        data.append(led_state[l3d_offset][2])
      self.controller.send_colors(start_l3d_offset, data)
      start_l3d_offset += self.controller.LED_PER_PACKET
    self.controller.send_refresh()

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
    row = button_id / 16
    index = button_id % 16
    return (row, index)

if __name__ == '__main__':
  LP = launchpad.Launchpad()
  LP.Open()

  controller = netl3d.netl3d(config.DEVICE_IP)

  try:
    animations(LP, controller)
  except KeyboardInterrupt:
    LP.Reset()
    LP.Close()
    raise

