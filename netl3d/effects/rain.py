import random
import time

from netl3d.base import FramePublisher
from netl3d.hardware.l3dcube import CubeFrame


def rain(frame: CubeFrame, fp: FramePublisher) -> None:
  rain_length = 4
  while True:
    x = random.randint(0, frame.face_size-1)
    start_y = random.randint(rain_length-1, frame.face_size-1)
    #start_y = random.randint(0, frame.face_size-1)
    z = random.randint(0, frame.face_size-1)

    frame.set_led((x, start_y, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-1, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(85.0/1000)
    frame.set_led((x, start_y-2, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(270.0/1000)

    frame.clear()
    frame.set_led((x, start_y-3, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(495.0/1000)
    frame.clear()

    frame.set_led((x, start_y, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-1, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(90.0/1000)
    frame.set_led((x, start_y-2, z), frame.get_color(1, 1, 1), verify_bounds=True)
    fp.publish(frame)
    time.sleep(765.0/1000)
    frame.clear()