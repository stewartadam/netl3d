# -*- coding: utf-8 -*-
from enum import Enum
import time
import threading
import uuid

from netl3d.hardware import l3dcube

class merge_strategy(Enum):
  OVERLAY = 1
  DIFFERNECE = 2
  ADD = 3
  SUBTRACT = 4
  EXCLUSIVE = 5
  AVERAGE = 6

class Simulator(threading.Thread):
  queued_animations = {}
  animations = {}
  signals = {}

  def __init__(self, stop_signal, controller, ticks_per_second=10):
    threading.Thread.__init__(self)
    self.signals['stop'] = stop_signal
    self.controller = controller
    self.led_state = l3dcube.CubeFrame()
    self.ticks_per_second = ticks_per_second
    self.tick_length = 1.0/ticks_per_second
    self.tick_num = 0

  def run(self):
    while not self.signals['stop'].is_set():
      self.led_state.clear()
      self.merge()
      self.controller.sync(self.led_state)

      time.sleep(self.tick_length)
      self.tick_num = (self.tick_num + 1) % self.ticks_per_second

  def add_animation(self, generator, strategy=merge_strategy.OVERLAY, priority=0, tick_multiplier=1):
    id = str(uuid.uuid4())
    self.queued_animations[id] = {
      'generator': generator,
      'priority': priority,
      'tick_multiplier': tick_multiplier,
      'merge_strategy': strategy,
    }
    self.sort_animations()
    return id

  def delete_animation(self, id):
    self.animations[id]['removal'] = True

  def sort_animations(self):
    self.animations = {k: v for k, v in sorted(self.animations.items(), key=lambda animation: animation[1]['priority'], reverse=True)}

  def merge(self):
    # Verify if we were asked to add new animations
    if self.queued_animations:
      for id, animation in self.queued_animations.items():
        self.animations[id] = animation
      self.sort_animations()

    # Render each animation
    for id in tuple(self.animations):
      animation = self.animations[id]

      # Verify if we were asked to remove an animation
      if 'removal' in animation:
        self.animations.pop(id)
        continue

      # If we are not meant to render this tick, copy prior frame
      animation_frame = None
      if self.tick_num*animation['tick_multiplier'] % 1 == 0:
        animation_frame = next(animation['generator'])
      else:
        if 'last_frame' in self.animations[id]:
          animation_frame = self.animations[id]['last_frame']
          animation['merge_strategy'] = merge_strategy.OVERLAY
        else:
          # animations that were recently added have no last_frame, so we should
          # render thier first frame and use it
          animation_frame = next(animation['generator'])
          animation['merge_strategy'] = merge_strategy.OVERLAY

      state = animation_frame._state_linear
      self.animations[id]['last_frame'] = animation_frame

      zero = self.led_state.get_color(0, 0, 0)
      if animation['merge_strategy'] == merge_strategy.OVERLAY:
        for i in range(len(state)):
          if self.led_state._state_linear[i].clamped_rgb == zero.clamped_rgb:
            self.led_state._state_linear[i] = state[i]
      elif animation['merge_strategy'] == merge_strategy.EXCLUSIVE:
        self.led_state._state_linear = state
        break
      elif animation['merge_strategy'] == merge_strategy.AVERAGE:
        for i in state:
          c1 = spectra.rgb(*(self.led_state[i]/255)).to("hsv")
          c2 = spectra.rgb(*(state[i]/255)).to("hsv")
          self.led_state._state_linear[i] = c1.blend(c2).clamped_rgb*255
