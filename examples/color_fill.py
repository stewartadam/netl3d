import sys

import config
import netl3d

def usage():
  print("Usage: color_fill.py r g b")
  print("\tWhere r, g and b are ints 0 - 255")
  sys.exit(1)

if len(sys.argv[1:]) != 3:
  usage()

try:
  rgb = [int(x) for x in sys.argv[1:]]
except ValueError:
  usage()

controller = netl3d.netl3d(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()

led = 0
while (led + 1 < controller.LED_NUM):
  data = bytearray()
  for i in range(controller.LED_PER_PACKET):
    data.append(rgb[0])
    data.append(rgb[1])
    data.append(rgb[2])
  controller.send_colors(led, data)
  led += controller.LED_PER_PACKET

print('Sending color %s' % rgb)
controller.send_refresh()
