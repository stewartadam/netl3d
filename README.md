netl3d
======
A small project that lets you control the 8x8x8 [L3D cube](http://www.lookingglassfactory.com/product/8x8x8-l3d-cube/) over the network.

Optionally, pair it with a [Novation Launchpad](https://global.novationmusic.com/launch/launchpad) and use it to play light on the cube.

## Features
- Works on Linux, OS X (Sierra) and Windows
- Graphing mode (8x 8x8 LED frames, so 1 current frame with 7 frames history)
- RGB test mode (cycles through colors)
- Launchpad control mode, tested with Launchpad MK1

Planned "soon":
- Lighting effect / animation library
- Scripted animations (think synced to music)

## Setup
1. Setup the Photon device embedded in your L3D cube and connect it to wifi. If you're not sure how to do this, see the official [L3D Cube](http://cubetube.org/docs/) or [Particle Photon](https://docs.particle.io/guide/getting-started/start/core/) documentation respectively.
2. Upload the included `netl3d.ino` firmware to your Photon device.
3. Determine the local IP address of your Particle by plugging it into your computer over USB and [monitor the serial output](https://docs.particle.io/reference/cli/#particle-serial-monitor). The netl3d firmware will print the Photon's local IP address once it connects to a network.
4. Recommended: configure a static DHCP reservation for your Particle to ensure it has a predicable IP address.

Your L3D cube is now ready to accept network instructions.

## Running the examples
Update `examples/config.py` with the Photon's IP address, then run any of the examples directly.

If you need to install dependencies (see below), I strongly recommend you do so in a venv, and via `pip`
```
python3 -m venv --system-site-packages netl3d
pip install ...
```

To activate the environment again later, run:
```
source netl3d/bin/activate
python examples/foo.py
```

The examples noted below have additional dependencies:
### `fft_pygame.py`
- [audiotools](http://audiotools.sourceforge.net/)
- [numpy](http://www.numpy.org/)
- [pygame](http://www.pygame.org/lofi.html)
- [pyaudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [scipy](https://www.scipy.org/)

Note: On OS X, you may receive an error installing pyaudio if you have installed its portaudio dependency with [Homebrew](brew.sh). It can be installed easily like this:
```
brew install portaudio
CFLAGS="-I/usr/local/include" LDFLAGS="-L/usr/local/lib" pip install pyaudio
```

### `launchpad_control.py`
- [pygame](http://www.pygame.org/lofi.html)
- [lauchpad.py](https://github.com/FMMT666/launchpad.py)

Note: pygame can be installed easily with `pip` on Linux/Windows, but I have had better luck with `brew install homebrew/python/pygame` on OS X (via [Homebrew](brew.sh)).

For now, use [my fork of lauchpad.py](https://github.com/stewartadam/launchpad.py) which has a fix for [issue #10](https://github.com/FMMT666/launchpad.py/issues/10) and allows launchpad.py to be used as a Python module. Run `python setup.py install` to install it to your site-packages folder.

If you have issues running the scripts, check the [Novation website](https://global.novationmusic.com/support/product-downloads) for drivers, if necessary. The launchpad needs to be recognized as a MIDI device when plugged in.
- On OS X, this can be verified by opening *Applications > Utilities > Audio MIDI Setup* and then selecting *Window > Show MIDI Studio*

Sometimes the Launchpad will glitch and stop responding. If that happens, press any one of the automap buttons (topmost 8 buttons) and try again. See documentation in the [FMMT666/lauchpad.py](https://github.com/FMMT666/launchpad.py) for additional known Launchpad-related compatibility issues and bugs.

#### LP Button mappings
Currently, supported buttons and their corresponding actions are:
- Up/Down: Control brightness (1/8 increments)
- Left/Right: Cycle colors (8-bit RGB color mask)
- Top right: Force-on all LEDs (takes precedence over others)
- Bottom right: Force-off all LEDs (takes precedence over others)
- Row 1: Produce a 8x8 pixel wall (zy-plane), offset on the L3D cube equal to the button index
- Row 2: Produce a 8x8 pixel slice (xz-plane), offset on the L3D cube equal to the button index
- row 3: Produce a 8x8 pixel sheet (xy-plane), offset on the L3D cube equal to the button index

## Resources
I found these resources helpful while writing this project:
- Understanding the Fast Fourier Transform: [Analyze audio using Fast Fourier Transform](http://stackoverflow.com/questions/604453/analyze-audio-using-fast-fourier-transform), [Python Scipy FFT wav files](http://stackoverflow.com/questions/23377665/python-scipy-fft-wav-files) and [How do I obtain the frequencies of each value in an FFT?](http://stackoverflow.com/questions/4364823/how-do-i-obtain-the-frequencies-of-each-value-in-an-fft)
- For scaling down the number of FFT bins from N down to 8: [Averaging over every n elements of a numpy array](http://stackoverflow.com/questions/15956309/averaging-over-every-n-elements-of-a-numpy-array) and [Reshape using a shape which is not a divisible factor of length of the list](http://stackoverflow.com/questions/10243878/reshape-using-a-shape-which-is-not-a-divisible-factor-of-length-of-the-list)
