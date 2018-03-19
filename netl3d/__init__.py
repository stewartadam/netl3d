# -*- coding: utf-8 -*-
"""
Interfaces with the Photon firmware to control a L3D cube over the network
"""
import binascii
import math
import socket

class netl3d:
  LED_NUM = 512
  LED_PER_PACKET = 256
  MAX_SEQUENCE_NUM = 256

  __brightness = 128
  __color_mask = 7
  __debug = False

  def __init__(self, device_ip='127.0.0.1', port=65506):
    self.device_ip = device_ip
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sequence_number = 0

  def set_debug(self, is_enabled):
    self.__debug = is_enabled

  def get_debug(self):
    return self.__debug

  def debug(self, message):
    if not self.get_debug():
      return
    print(message)

  def handshake(self):
    data = bytearray()
    data.append(self.sequence_number)
    self.send_packet(0, data)

  def send_colors(self, start_led, pixel_data):
    data = bytearray()
    data.append(start_led >> 8)
    data.append(start_led % 256)
    data += pixel_data
    self.send_packet(1, data)

  def send_refresh(self):
    self.send_packet(2)

  def send_packet(self, control_value, data=None):
    headers = bytearray()
    headers.append(control_value)
    headers.append(self.sequence_number)
    payload = headers + data if data else headers

    self.debug("Payload length: %d" % len(payload))
    self.debug("Message: %s" % binascii.hexlify(payload))

    self.socket.sendto(payload, (self.device_ip, self.port))
    self.sequence_number = (self.sequence_number + 1) % netl3d.MAX_SEQUENCE_NUM

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
    return [r*br*r_mask, g*br*g_mask, b*br*b_mask]
