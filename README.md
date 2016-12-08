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

## Installation
1. Setup the Photon device embedded in your L3D cube and connect it to wifi. If you're not sure how to do this, see the official [L3D Cube](http://cubetube.org/docs/) or [Particle Photon](https://docs.particle.io/guide/getting-started/start/core/) documentation respectively.
2. Upload the included `netl3d.ino` firmware to your Photon device.
3. Determine the local IP address of your Particle by plugging it into your computer over USB and [monitor the serial output](https://docs.particle.io/reference/cli/#particle-serial-monitor). The netl3d firmware will print the Photon's local IP address once it connects to a network.
4. Update `config.py` with the Photon's IP address
5. Recommended: configure a static DHCP reservation for your Particle to ensure it has a predicable IP address.
6. Run one of the `l3d_foo.py` scripts included

## Optional: launchpad control
To use a Launchpad to control the L3D cube, grab a copy of the [FMMT666/lauchpad.py](https://github.com/FMMT666/launchpad.py) repo using this [master as ZIP download](https://github.com/FMMT666/launchpad.py/archive/master.zip) link and unpack the files into this repo, i.e. so that `launchpad.py` rests in the same folder as `netl3d.py`. This manual step is necessary due to the naming of launchpad.py, (see [launchpad.py issue #10](https://github.com/FMMT666/launchpad.py/issues/10)).

Next, install the launchpad.py dependency `pygame` with `pip install pygame` on Linux/Windows or `brew install homebrew/python/pygame` on OS X (via [Homebrew](brew.sh))

If you have issues running the scripts, check the [Novation website](https://global.novationmusic.com/support/product-downloads) for drivers, if necessary. The launchpad needs to be recognized as a MIDI device when plugged in.
- On OS X, this can be verified by opening *Applications > Utilities > Audio MIDI Setup* and then selecting *Window > Show MIDI Studio*

#### LP Button mappings
Currently, supported buttons and their corresponding actions are:
- Up/Down: Control brightness (1/8 increments)
- Left/Right: Cycle colors (8-bit RGB color mask)
- Top right: Force-on all LEDs (takes precedence over others)
- Bottom right: Force-off all LEDs (takes precedence over others)
- Row 1: Produce a 8x8 pixel wall (zy-plane), offset on the L3D cube equal to the button index
- Row 2: Produce a 8x8 pixel slice (xz-plane), offset on the L3D cube equal to the button index
- row 3: Produce a 8x8 pixel sheet (xy-plane), offset on the L3D cube equal to the button index

## Known Issues
Sometimes the Launchpad will glitch and stop responding. If that happens, press any one of the automap buttons (topmost 8 buttons) and try again. See documentation in the [FMMT666/lauchpad.py](https://github.com/FMMT666/launchpad.py) for additional known Launchpad-related compatibility issues and bugs.
