# -*- coding: utf-8 -*-
from enum import Enum
import time
import uuid

class merge_strategy(Enum):
  OVERLAY = 1
  DIFFERNECE = 2
  ADD = 3
  SUBTRACT = 4
  EXCLUSIVE = 5
  AVERAGE = 6

class simulator:
  animations = []

  def __init__(self, controller, led_state, ticks_per_second=10):
    self.controller = controller
    self.led_state = led_state
    self.ticks_per_second = ticks_per_second
    self.tick_length = 1.0/ticks_per_second

  def run(self):
    while True:
      self.led_state.clear()
      self.merge()
      self.led_state.sync()

      time.sleep(self.tick_length)

  def add_animation(self, generator, strategy=merge_strategy.OVERLAY, priority=0):
    id = uuid.uuid4()
    self.animations.append({
      'id': id,
      'generator': generator,
      'priority': priority,
      'merge_strategy': strategy,
    })
    self.sort_animations()
    return id

  def delete_animation(self, id):
    for animation in animations:
      if animation['id'] == id:
        animations.remove(animations)

  def sort_animations(self):
    self.animations.sort(key=lambda animation: animation['priority'], reverse=True)

  def merge(self):
    for animation in self.animations:
      print(animation)
      tmp = next(animation['generator'])
      state = tmp.led_state
      zero = self.controller.get_color(0, 0, 0)

      if animation['merge_strategy'] == merge_strategy.OVERLAY:
        for i in range(len(state)):
          if self.led_state.led_state[i] == zero:
            self.led_state.led_state[i] = state[i]
      elif animation['merge_strategy'] == merge_strategy.EXCLUSIVE:
        self.led_state.led_state = state
        break
      elif animation['merge_strategy'] == merge_strategy.AVERAGE:
        for i in state:
          c1 = spectra.rgb(*(self.led_state[i]/255)).to("hsv")
          c2 = spectra.rgb(*(state[i]/255)).to("hsv")
          self.led_state.led_state[i] = c1.blend(c2).clamped_rgb*255

      tmp.clear()
