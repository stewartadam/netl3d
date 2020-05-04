#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes system microphone input (no parameters) or an audio file (with parameter)
and performs frequency analysis on the samples read.
"""
import audiotools
import numpy
import pyaudio
import pygame
import scipy
import spectra
import sys
import time

import netl3d
from netl3d.hardware import l3dcube

# audio settings
SAMPLES = 192 # length of sample
RATE = 44100 # bitrate to record
BITS_PER_SAMPLE = 16
HISTORY_SIZE = 120

# visualization settings
WIDTH = 640
HEIGHT = 400
FPS = 30

# TARGET_BIN_COUNT must be a power of 2 for channel reduction math to work out right
TARGET_BIN_COUNT = 32

config = netl3d.parse_config()
netl3d.configure_logging(config)
ip = config['hardware']['l3dcube']['ip']
port = config['hardware']['l3dcube']['port']

controller = l3dcube.L3DGraphController(ip, port)
controller.handshake()

clock = pygame.time.Clock()
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))

# The two PCM frame providers, one for mic input and the other for decoding a file stream
# We expect 4x samples back in bytes of raw pcm input (16 bits (2 bytes) per sample, and 2 channels)
def stream_input(in_stream):
  num_frames = int(SAMPLES * BITS_PER_SAMPLE / 8)
  pcm = in_stream.read(num_frames, exception_on_overflow=False)
  pcm_list = numpy.fromstring(pcm, dtype=numpy.int16)
  frames = audiotools.pcm.from_list(pcm_list, 2, 16, True)
  return frames

def stream_file(in_stream):
  # We loop on read because mp3 (and possibly other formats) max
  bytes_decoded = 0
  frames = audiotools.pcm.empty_framelist(2, 16)
  t1 = time.time()
  while bytes_decoded < SAMPLES * BITS_PER_SAMPLE:
    num_frames = int(SAMPLES * BITS_PER_SAMPLE / 8)
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

fft_history = numpy.zeros(shape=(HISTORY_SIZE, TARGET_BIN_COUNT))
fft_history.fill(1)
SCALE_FACTORS = fft_history[0]
GLOBAL_LOUDNESS = 1

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
          in_stream.read(SAMPLES * BITS_PER_SAMPLE)

  t1 = time.time()

  frames = stream_provider(in_stream)
  if frames.frames == 0:
    quit()
  pcm = frames.to_bytes(False, True)
  if output:
    out_stream.write(pcm)

  # Average the two 4096-byte channels for a single 4096-byte stream
  # Note with 16bit streams 4096 bytes is only 2048 samples
  pcm0 = frames.channel(0).to_bytes(False, True)
  pcm0_np = numpy.fromstring(pcm0, dtype=numpy.int16)
  pcm1 = frames.channel(1).to_bytes(False, True)
  pcm1_np = numpy.fromstring(pcm1, dtype=numpy.int16)
  pcm_mono_avg_np = numpy.mean(numpy.array([pcm0_np, pcm1_np]), axis=0)
  # if we had mono input, we could convert from a bytestring this way:
  #signal = numpy.fromstring(pcm0, dtype=numpy.int16)
  signal = pcm_mono_avg_np

  # normalize signal on [-1,1]
  normalized = [(ele/2**BITS_PER_SAMPLE)*2-1 for ele in signal]

  fft = abs(scipy.fft(normalized))
  if iteration == 1:
    num_bins = SAMPLES / 2
    max_hz = RATE / 2
    bin_size = max_hz / num_bins
    print('%d sample rate with %d samples yields %d bins of %.1f Hz (0 - %d Hz)' % (RATE, SAMPLES, num_bins, bin_size, max_hz))

  # FFT is symmetrical & first (and therefore last) channels are Nyquist frequencies
  fft = fft[1:-1]
  fft_len = len(fft) // 2
  fft = fft[:fft_len]
  # Duplicate last channel so we have an array length with a nice power of 2
  fft = numpy.append(fft, fft[-1])

  # Truncate 10kHz-20KHz range
  fft_len = len(fft) // 2
  fft = fft[:fft_len]

  # Truncate 5kHz-10kHz range
  fft_len = len(fft) // 2
  fft = fft[:fft_len]

  # Truncate 2.5kHz-5kHz range
  fft_len = len(fft) // 2
  fft = fft[:fft_len]

  try:
    window_sz = len(fft) // TARGET_BIN_COUNT
    window_sz_cube = len(fft) // 8

    # Group the FFT channels into lists of size window_sz and average the groups
    # to get target number of channels to display
    fft_grouped = [fft[i:(i+window_sz)] for i in range(0, len(fft), window_sz)]
    fft_grouped_cube = [fft[i:(i+window_sz_cube)] for i in range(0, len(fft), window_sz_cube)]
    fft = numpy.mean(fft_grouped, axis=1)
    fft_cube = numpy.mean(fft_grouped_cube, axis=1)
  except:
    params = (len(fft), len(signal), len(pcm))
    print('ERROR: Could not reshape FFT array of len %d. signal=%d, pcm=%d' % params)
    raise

  for x in range(TARGET_BIN_COUNT):
    # see note about other divisor below
    divisor = max(SCALE_FACTORS[x], (SCALE_FACTORS[x]+GLOBAL_LOUDNESS)/2)
    # left top width height
    rect = (x*WIDTH/TARGET_BIN_COUNT, 0, WIDTH/TARGET_BIN_COUNT, max(1, fft[x]/divisor*HEIGHT))
    try:
      pygame.draw.rect(surface, (255, 0, 0), rect)
    except:
      print("ERROR: could not draw rect: l=%s t=%s w=%s h=%s" % rect)
      raise
  pygame.display.update()
  clock.tick(FPS)

  frame = l3dcube.GraphFrame()

  window_sz_cube = TARGET_BIN_COUNT//frame.face_size
  grouped = [SCALE_FACTORS[i:(i+window_sz_cube)] for i in range(0, len(SCALE_FACTORS), window_sz_cube)]
  SCALE_FACTORS_CUBE = numpy.mean(grouped, axis=1)

  for x in range(frame.face_size):
    frame.set_color_mask(x if x > 0 else 7)
    # Bass has a significantly higher value for some reason, so take the larger of the average between channel and loudness (so a generally loud song will dampen a quiet bin) or the channel itself (for the lower bass bins)
    divisor = max(SCALE_FACTORS_CUBE[x], (SCALE_FACTORS_CUBE[x]+GLOBAL_LOUDNESS)/2)
    threshold = fft_cube[x]/divisor*frame.face_size
    for y in range(frame.face_size):
      frame.set_led((x, y), frame._apply_masks(spectra.rgb(1, 1, 1)) if y <= threshold else spectra.rgb(0, 0, 0))
    frame.set_color_mask(7)
  controller.sync(frame)

  # Build a history of fft values to determine a 'loudness' scale factor
  tmp_fft_history = numpy.ndarray((HISTORY_SIZE, TARGET_BIN_COUNT))
  for i in range(len(fft_history)-1):
    tmp_fft_history[i+1] = fft_history[i]

  min_values = numpy.zeros(TARGET_BIN_COUNT)
  min_values.fill(1)

  tmp_fft_history[0] = numpy.maximum(fft, min_values)
  fft_history = tmp_fft_history

  # Column-wise max (max value for each bin)
  SCALE_FACTORS = numpy.max(fft_history, axis=0)
  # Average loudness of all bins
  GLOBAL_LOUDNESS = numpy.average(SCALE_FACTORS)

  if iteration % 20 == 0:
    print ('SCALE FACTORS (max scale factor, current fft):')
    for i in range(TARGET_BIN_COUNT):
      print('%.1f, %.1f' % (SCALE_FACTORS[i], fft_history[0][i]))
    print("GLOBAL LOUDNESS = %.1f" % GLOBAL_LOUDNESS)
