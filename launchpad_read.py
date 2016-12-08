# -*- coding: utf-8 -*-
"""
Debugs which button is currently pressed on the Launchpad by printing the button
details to the console, and lighting up any pressed buttons on the launchpad.
"""
import launchpad

def main(LP):
  while 1:
    pygame.time.wait(5)

    but = LP.ButtonStateRaw()
    if but != []:
      # button ID is 16*row + index
      button_id = but[0]
      row = button_id / 16
      index = button_id % 16 + row
      pressed = but[1]
      print '%s: bid=%d, row=%d, index=%d, pressed=%s' % (but, button_id, row, index, pressed)

      if but[1]:
        LP.LedCtrlRaw(but[0], 0, 3)
      else:
        LP.LedCtrlRaw(but[0], 0, 0)

  LP.Reset() # turn all LEDs off
  LP.Close() # close the Launchpad

if __name__ == '__main__':
  LP = launchpad.Launchpad()
  LP.Open()

  try:
    main(LP)
  except KeyboardInterrupt:
    LP.Reset()
    LP.Close()
    raise

