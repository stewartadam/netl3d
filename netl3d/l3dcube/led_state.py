import netl3d.led_state

class led_state(netl3d.led_state):
  def __init__(self, controller, size=8):
    super(led_state, self).__init__(controller)
    self.size = size

  def get_point_index(self, x, y, z):
    """Gets the offset on the 1D LED state array given 3D point co-ordinates"""
    return x*(self.size**2) + y*self.size + z

  def get_point(self, x, y, z):
    """Returns the LED state at the given 3D point co-ordinates"""
    return self.led_state[self.get_point_index(x, y, z)]

  def set_point(self, x, y, z, state):
    """Sets the LED state at the given 3D point co-ordinates"""
    self.led_state[self.get_point_index(x, y, z)] = state

  def fill(self, color=[0, 0, 0]):
    self.led_state = [color]*self.controller.LED_NUM

  def sync(self):
    """Synchronizes in-memory LED state with device"""
    start_l3d_offset = 0
    while (start_l3d_offset < len(self.led_state)):
      data = bytearray()
      for i in range(self.controller.LED_PER_PACKET):
        l3d_offset = start_l3d_offset + i
        data.append(self.led_state[l3d_offset][0])
        data.append(self.led_state[l3d_offset][1])
        data.append(self.led_state[l3d_offset][2])
      self.controller.send_colors(start_l3d_offset, data)
      start_l3d_offset += self.controller.LED_PER_PACKET
    self.controller.send_refresh()