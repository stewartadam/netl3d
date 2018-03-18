#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes system microphone input (no parameters) or an audio file (with parameter)
and performs frequency analysis on the samples read.
"""
import scipy
import pyaudio
import numpy
import time
import pygame
import sys
import audiotools

import config
import netl3d
from netl3d.l3dcube import graph

# audio settings
BUFFER = 4096 # length of sample
RATE = 44100 # bitrate to record
BITS_PER_SAMPLE = 16
HISTORY_SIZE = 30

# visualization settings
WIDTH = 640
HEIGHT = 400
FPS = 30
SCALE_FACTOR = 5

controller = netl3d.netl3d(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()
g = graph(controller)

clock = pygame.time.Clock()
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))

# The two PCM frame providers, one for mic input and the other for decoding a file stream
# We expect 8192 bytes of raw pcm input (16 bits/sample, 2048 samples for each of the 2 channels)
def stream_input(in_stream):
  num_frames = int(BUFFER / (BITS_PER_SAMPLE / 8))
  pcm = in_stream.read(num_frames, exception_on_overflow=False)
  pcm_list = numpy.fromstring(pcm, dtype=numpy.int16)
  frames = audiotools.pcm.from_list(pcm_list, 2, 16, True)
  return frames

def stream_file(in_stream):
  # We loop on read because mp3 (and possibly other formats) max
  bytes_decoded = 0
  frames = audiotools.pcm.empty_framelist(2, 16)
  t1 = time.time()
  while bytes_decoded < BUFFER:
    num_frames = int(BUFFER / (BITS_PER_SAMPLE / 8))
    frames = frames + in_stream.read(num_frames)
    bytes_decoded += num_frames * (frames.bits_per_sample/8) / frames.channels
  return frames

p = pyaudio.PyAudio()

output = False
if len(sys.argv[1:]):
  stream = audiotools.open(sys.argv[1])
  in_stream = stream.to_pcm()
  stream_provider = stream_file
  output = True
else:
  in_stream = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True)
  stream_provider = stream_input

# open output stream to playback something
out_stream = p.open(format =
    p.get_format_from_width(pyaudio.paInt32),
    channels = 2,
    rate = RATE,
    output = True)

means = numpy.ndarray(HISTORY_SIZE)
means.fill(0)

def quit():
  in_stream.close()
  out_stream.close()
  p.terminate()
  pygame.quit()
  sys.exit()

iteration = 0
while True:
  iteration += 1
  surface.fill((16, 16, 16))

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      quit()
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RIGHT:
        print("Seeking...")
        for i in range(300):
          in_stream.read(BUFFER)

  t1 = time.time()

  frames = stream_provider(in_stream)
  if frames.frames == 0:
    quit()
  pcm = frames.to_bytes(False, True)
  pcm0 = frames.channel(0).to_bytes(False, True)
  pcm1 = frames.channel(1).to_bytes(False, True)
  if output:
    out_stream.write(pcm)

  duration = time.time() - t1

  # We expect 4096 bytes in "signal" after transform
  signal = numpy.fromstring(pcm, dtype=numpy.int16)

  normalized = [(ele/2**BITS_PER_SAMPLE)*2-1 for ele in signal] # normalized on [-1,1]
  fft_orig = abs(scipy.fft(normalized))
  fft_orig_len = int(len(fft_orig)/2) # fft is symmetrical for our purposes

  # throw away first channel (average of all channels), and last to make the set even
  fft = fft_orig[1:fft_orig_len-1]
  # we care more about the lower channels
  fft = fft[:int(len(fft)/16)]

  try:
    num_channels = 8
    window_sz = int((len(fft)/num_channels))
    fft_grouped = [fft[i:(i+window_sz)] for i in range(0, len(fft), window_sz)]
    fft_grouped[0] = fft_grouped[0]/3 # tone down the bass a bit
    fft_grouped[-1] = numpy.resize(fft_grouped[-1], window_sz)
    fft_means = numpy.mean(fft_grouped, axis=1)
    #fft = fft.reshape(-1, window_sz).mean(axis=1)[1:-2]
    fft = fft_means
  except:
    params = (len(fft), len(signal), len(pcm))
    print('ERROR: Could not reshape FFT array of len %d. signal=%d, pcm=%d' % params)
    raise

  if iteration == 1:
    for i in range(int(len(fft))):
      bin_size = RATE / BUFFER * (fft_orig_len / num_channels)
      print('%d: %d Hz' % (i, bin_size*i))
      first = True

  points_fft = numpy.column_stack((range(len(fft)), fft))

  for i in range(len(points_fft)):
    # left top width height
    rect = (i*WIDTH/len(points_fft), 0, WIDTH/len(points_fft), points_fft[i][1]/SCALE_FACTOR*HEIGHT)
    try:
      pygame.draw.rect(surface, (255, 0, 0), rect)
    except:
      print("ERROR: could not draw rect: l=%s t=%s w=%s h=%s" % rect)
      raise

  frame = []
  for i in range(8):
    row = []
    for j in range(8):
      controller.set_color_mask(j if j > 0 else 7)

      point = points_fft[j][1]
      threshold = i/8.0*SCALE_FACTOR

      row.append(controller.get_color(1, 1, 1) if point >= threshold else [0, 0, 0])
    frame.append(row)

  current_means = numpy.ndarray(HISTORY_SIZE)
  for i in range(len(means)-1):
    current_means[i+1] = means[i]
  current_means[0] = numpy.max(fft)

  means = current_means
  SCALE_FACTOR = max(numpy.max(means), 1)

  if iteration % 5 == 0:
    print('point=%s, th=%s' % (point, SCALE_FACTOR))

  pygame.display.update()
  g.slide(frame)
  clock.tick(FPS)
  # tick_busy_loop for accuracy
