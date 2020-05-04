import datetime
import tty
import sys
import termios

orig_settings = termios.tcgetattr(sys.stdin)

tty.setcbreak(sys.stdin)
x = 0
try:
  start_time = datetime.datetime.now()
  while True:
    keypress = sys.stdin.read(1)[0]
    end_time = datetime.datetime.now()
    delta = end_time - start_time

    if ord(keypress) == 10: # newline
      print()
    else: # we don't want to skew last keypress time when we read a newline
      ms = delta.microseconds/1000
      print(ms, end=',')
      start_time = end_time

except KeyboardInterrupt:
  termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)


