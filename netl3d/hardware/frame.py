import spectra

class Frame:
  """
  Interface and common functions for hardware-specific LED frames. Maintains
  an in-memory LED state that can be synchronized to a device.
  """
  _brightness_mask = 0.8
  _color_mask = 7

  def __init__(self):
    self.clear()

  def _apply_masks(self, color):
    """Returns the LED state at the given pos, applying any masks"""
    br_mask = self._brightness_mask or 1.0
    (r, g, b) = color.clamped_rgb
    (r_mask, g_mask, b_mask) = self.get_color_mask()
    return spectra.rgb(r*br_mask*r_mask, g*br_mask*g_mask, b*br_mask*b_mask)

  def get_led(self, pos):
    """Returns the LED state at the given pos, applying any masks"""
    return self._apply_masks(self.get_led_raw(pos))

  def get_led_raw(self, pos):
    """Returns the LED state at the given pos"""
    raise NotImplementedError

  def set_led(self, pos, state):
    """Sets the LED state at the given pos"""
    raise NotImplementedError

  def fill(self, color):
    raise NotImplementedError

  def clear(self):
    self.fill(spectra.rgb(0,0,0).to('hsv'))

  def get_brightness_mask(self):
    return self._brightness_mask

  def set_brightness_mask(self, brightness_mask):
    if brightness_mask < 0:
      brightness_mask = 0
    elif brightness_mask > 1:
      brightness_mask = 1
    self._brightness_mask = brightness_mask

  def adjust_brightness_mask(self, increment):
    self.set_brightness_mask(self.get_brightness_mask() + increment)

  def get_color_mask(self):
    """Returns a (r,g,b) tuple valued with 1 or 0"""
    r = (self._color_mask >> 2) % 2 == 1
    g = (self._color_mask >> 1) % 2 == 1
    b = self._color_mask % 2 == 1
    return (r, g, b)

  def set_color_mask(self, mask):
    self._color_mask = mask % 8

  def adjust_color_mask(self, increment):
    self.set_color_mask(self._color_mask + increment)
    if self._color_mask == 0:
      self.adjust_color_mask(increment)
