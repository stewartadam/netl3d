# -*- coding: utf-8 -*-
"""
Interfaces with the Photon firmware to control a L3D cube over the network. L3D
cube hardware indexes at the start far back, bottom right corner and count
upward, wrapping to the right, then forward.
"""
import binascii
import math
import socket

import netl3d
from .frame import CubeFrame
from .frame import GraphFrame
from .shapes import Shapes

class Controller(netl3d.Controller):
  LED_NUM = 512
  LED_PER_PACKET = 256
  MAX_SEQUENCE_NUM = 256

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
    self.debug("Sending handshake with sequence %d" % self.sequence_number)
    data = bytearray()
    data.append(self.sequence_number)
    self.send_packet(0, data)

  def send_colors(self, start_led, pixel_data):
    self.debug("Sending color data starting with LED %d" % start_led)
    data = bytearray()
    data.append(start_led >> 8)
    data.append(start_led % 256)
    data += pixel_data
    self.send_packet(1, data)

  def send_refresh(self):
    self.debug("Sending refresh command")
    self.send_packet(2)

  def send_packet(self, control_value, data=None):
    headers = bytearray()
    headers.append(control_value)
    headers.append(self.sequence_number)
    payload = headers + data if data else headers

    self.debug("Payload length: %d" % len(payload))
    self.debug("Message: %s" % binascii.hexlify(payload))

    self.socket.sendto(payload, (self.device_ip, self.port))
    self.sequence_number = (self.sequence_number + 1) % self.MAX_SEQUENCE_NUM

  def sync(self, cubeFrame):
    """Synchronizes in-memory LED state with device"""
    leds_in_packet = 0
    packet_num = 0
    data = bytearray()
    # See note at top about L3D cube hardware indexing
    for z in reversed(range(cubeFrame.face_size)):
      for x in range(cubeFrame.face_size):
        for y in range(cubeFrame.face_size):
          pos = (x, y, z)
          color = cubeFrame.get_led(pos)

          (r,g,b) = tuple(int(x*255) for x in color.clamped_rgb)
          data.append(r)
          data.append(g)
          data.append(b)

          leds_in_packet += 1
          if (leds_in_packet >= self.LED_PER_PACKET):
            self.send_colors(packet_num * self.LED_PER_PACKET, data)
            leds_in_packet = 0
            packet_num += 1
            data = bytearray()
    self.send_refresh()

class GraphController(Controller):
  """
  Basic support for 'graphing' using the L3D cube; new 8x8 frames of lighting can
  be inserted at the front and existing frames are shifted back, with the last
  (now 9th) frame being popping from memory.
  """
  cubeFrame = CubeFrame()

  def __init__(self, device_ip='127.0.0.1', port=65506):
    Controller.__init__(self, device_ip, port)

  def sync(self, graphFrame):
    # See note at top about L3D cube hardware indexing
    for x in range(self.cubeFrame.face_size):
      for y in range(self.cubeFrame.face_size):
        for z in reversed(range(1, self.cubeFrame.face_size)):
          # Starts at backmost frame, copies LED state from frame ahead
          self.cubeFrame.set_led((x, y, z), self.cubeFrame.get_led_raw((x, y, z-1)))

    for x in range(graphFrame.face_size):
      for y in range(graphFrame.face_size):
        self.cubeFrame.set_led((x, y, 0), graphFrame.get_led((x, y)))

    Controller.sync(self, self.cubeFrame)
