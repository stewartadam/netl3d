import binascii
import math
import socket

class netl3d:
  LED_NUM = 512
  LED_PER_PACKET = 256

  brightness = 128
  color_mask = 7
  debug = False
  debug_net = False

  def __init__(self, device_ip='127.0.0.1', port=65506):
    self.device_ip = device_ip
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def send_colors(self, start_led, data):
    header = bytearray()
    header.append(start_led >> 8)
    header.append(start_led % 256)
    self.send_packet(header+data)

  def send_refresh(self):
    header = bytearray()
    header.append(2)
    self.send_packet(header)

  def send_packet(self, payload):
    if self.debug or self.debug_net:
      print "Payload length:", len(payload)
      print "Message:", binascii.hexlify(payload)
    self.socket.sendto(payload, (self.device_ip, self.port))

  def get_brightness(self, ):
    return self.brightness

  def set_brightness(self, brightness):
    if brightness < 0:
      brightness = 0
    elif brightness > 255:
      brightness = 255
    self.brightness = brightness

  def adjust_brightness(self, increment):
    self.set_brightness(self.get_brightness() + increment)

  def get_color_mask(self):
    """Returns a (r,g,b) tuple valued with 1 or 0"""
    r = (self.color_mask >> 2) % 2 == 1
    g = (self.color_mask >> 1) % 2 == 1
    b = self.color_mask % 2 == 1
    return (r, g, b)

  def set_color_mask(self, mask):
    self.color_mask = mask % 8

  def adjust_color_mask(self, increment):
    self.set_color_mask(self.color_mask + increment)
    if self.color_mask == 0:
      self.adjust_color_mask(increment)

  def get_color(self, r, g, b, a=None):
    br = self.brightness if a is None else a
    (r_mask, g_mask, b_mask) = self.get_color_mask()
    return [r*br*r_mask, g*br*g_mask, b*br*b_mask]
