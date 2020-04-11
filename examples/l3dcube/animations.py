# -*- coding: utf-8 -*-
"""
Orchestrates individual shapes into animations, rotation animations every 10s
"""
import itertools
import pygame
import random
import time

import netl3d
from netl3d.hardware import l3dcube

def random_col(frame, speed=0.5):
  while True:
    x = random.randint(0, frame.face_size-1)
    y = random.randint(0, frame.face_size-1)
    l3dcube.shapes.column(x, y, frame.get_color(1, 0, 1, 255), frame)
    time.sleep(speed)
    frame.clear()

def rain(frame):
  rain_length = 4
  while True:
    x = random.randint(0, frame.face_size-1)
    start_y = random.randint(rain_length-1, frame.face_size-1)
    #start_y = random.randint(0, frame.face_size-1)
    z = random.randint(0, frame.face_size-1)

    frame.set_led((x, start_y, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-1, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(85.0/1000)
    frame.set_led((x, start_y-2, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(270.0/1000)

    frame.clear()
    frame.set_led((x, start_y-3, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(495.0/1000)
    frame.clear()

    frame.set_led((x, start_y, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-1, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-2, z), frame.get_color(1, 1, 1), verify_bounds=True)
    time.sleep(765.0/1000)
    frame.clear()

def strobe(frame, speed=0.05):
  while True:
    l3dcube.shapes.solid_fill(frame.get_color(1, 1, 1, 255), frame=frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.solid_fill(frame.get_color(1, 1, 1, 0), frame=frame)
    time.sleep(speed)
    frame.clear()

def outer_square(frame, speed=0.25):
  while True:
    l3dcube.shapes.wall(0, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.slice(7, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.wall(7, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.slice(0, frame)
    time.sleep(speed)
    frame.clear()
    frame.adjust_color_mask(1)

def expanding_cube(frame, speed=0.1):
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      l3dcube.shapes.centered_cube(i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()

def heartbeat_cube(frame, speed=0.1):
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      l3dcube.shapes.centered_cube(i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()
    for i in range(2, 7, 2):
      l3dcube.shapes.centered_cube(8-i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()

def pulse(frame, speed=0.5):
  # Terrible way of going about this, but it works for now/demo purposes
  while True:
    frame.adjust_color_mask(1)
    # frame length, target brightness
    steps = [(2, .9), (0, None), (7, .2)]
    num_frames = sum([x[0] for x in steps])
    for i in range(num_frames):
      if i <= steps[0][0]:
        length = steps[0][0]
        brightness = steps[0][1]
        brightness = i/length * brightness + 0.1
      # elif i > steps[0][0] and i <= steps[0][0] + steps[1][0]:
      #   start = steps[0][0] + 1
      #   length = steps[1][0]
      #   brightness = 1-steps[0][1]
      #   start_brightness = steps[0][1] + 0.1
      #   brightness = (i-start)/length * brightness + start_brightness
      else:
        start = (num_frames - steps[2][0]) + 1
        length = steps[2][0]
        inverse_brightness = 1 - steps[2][1]
        brightness = 1 - ( (i-start)/length * inverse_brightness )
      frame.set_brightness_mask(brightness)
      l3dcube.shapes.centered_cube(8, frame=frame, fill=True)
      time.sleep(speed)
      frame.clear()
