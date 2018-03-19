import spectra
import sys

import config
from netl3d.hardware import l3dcube

def usage():
  print("Usage: color_fill.py r g b")
  print("\tWhere r, g and b are ints 0 - 255")
  sys.exit(1)

if len(sys.argv[1:]) != 3:
  usage()

try:
  rgb = [float(x)/255 for x in sys.argv[1:]]
except ValueError:
  usage()

controller = l3dcube.Controller(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()

color = spectra.rgb(*rgb)
print('Sending color %s' % color.hexcode)
frame = l3dcube.CubeFrame()
frame.fill(color)
controller.sync(frame)
