import threading
import time
from typing import Dict

import spectra

from netl3d.base import FrameTransform
from netl3d.base import FramePublisher
from netl3d.hardware.l3dcube import CubeFrame

class FrameFadeTransform(FrameTransform):
  def __init__(self, fade_time_ms: int, start_opacity: float = 1.0, end_opacity: float = 0.0):
    if (fade_time_ms <= 0):
      raise ValueError("Fade time must be a non-zero, positive value.")
    if (start_opacity < 0.0 or start_opacity > 1.0):
      raise ValueError("Start opacity must be a float between [0, 1]")
    if (end_opacity < 0.0 or end_opacity > 1.0):
      raise ValueError("End opacity must be a float between [0, 1]")

    self.fade_time_ms = fade_time_ms
    self.start_opacity = start_opacity
    self.end_opacity = end_opacity
    self.start_time = time.monotonic()

  def apply(self, input: CubeFrame) -> CubeFrame:
      output = CubeFrame()
      progress_ratio = min(1.0, (time.monotonic() - self.start_time)*1000/self.fade_time_ms)
      current_opacity = self.start_opacity + (self.end_opacity - self.start_opacity)*progress_ratio

      for i in range(len(input._state_linear)):
        (r, g, b) = input._state_linear[i].clamped_rgb
        output._state_linear[i] = spectra.rgb(r*current_opacity, g*current_opacity, b*current_opacity)
      return output

class LEDFadeTransform(FrameTransform):
  def __init__(self, fade_time_ms: int, start_opacity: float = 1.0, end_opacity: float = 0.0):
    if (fade_time_ms <= 0):
      raise ValueError("Fade time must be a non-zero, positive value.")
    if (start_opacity < 0.0 or start_opacity > 1.0):
      raise ValueError("Start opacity must be a float between [0, 1]")
    if (end_opacity < 0.0 or end_opacity > 1.0):
      raise ValueError("End opacity must be a float between [0, 1]")

    self.fade_time_ms = fade_time_ms
    self.start_opacity = start_opacity
    self.end_opacity = end_opacity
    self.start_time = time.monotonic()

    self.fading: Dict[int, object] = {} # FIXME typing

  def apply(self, input: CubeFrame) -> CubeFrame:
      output = CubeFrame()

      # Copy presently fading LEDs into ouput frame
      current_fading = dict(self.fading)
      for i, data in current_fading.items():
        if time.monotonic() > data['start_time'] + self.fade_time_ms/1000:
          # Remove state for LEDs that have completely faded
          print(f'popping {i}')
          self.fading.pop(i)
        else:
          # Calculate brightness and set faded LED on output
          progress_ratio = (time.monotonic() - data['start_time'])*1000 / self.fade_time_ms
          current_opacity = self.start_opacity + (self.end_opacity - self.start_opacity)*progress_ratio
          print(f'copying {i} @ {progress_ratio}% = {current_opacity}x brightness')
          (r, g, b) = data['color'].clamped_rgb
          output._state_linear[i] = spectra.rgb(r*current_opacity, g*current_opacity, b*current_opacity)

      # Copy active LEDs from input frame to output, marking them as due for fading in future frames
      for i in range(len(input._state_linear)):
        if input._state_linear[i].clamped_rgb != (0.0, 0.0, 0.0):
          print(f'setting {i}')
          self.fading[i] = {
            'start_time': time.monotonic(),
            'color': input._state_linear[i],
          }
          output._state_linear[i] = input._state_linear[i]

      return output