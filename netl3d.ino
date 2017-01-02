/**
 * Firmware to allow (relatively) efficient network control of an L3D cube
 */
#include "neopixel/neopixel.h"

#define ENABLE_DEBUG            FALSE

#define SIDE                    8   //8x8x8 Cube size
#define PIXELS_PER_PANEL        (PIXEL_CNT / SIDE)
#define BPP                     3       //3 bytes per pixel or 24bit (RGB)
#define PI                      3.1415926535

#define UDP_PORT                65506
#define MAX_PACKET_SIZE         1500

//NEOPIXEL Defines
#define PIXEL_CNT               (SIDE*SIDE*SIDE)
#define PIXEL_PIN               D0
#define PIXEL_TYPE              WS2812B

UDP Udp;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(PIXEL_CNT, PIXEL_PIN, PIXEL_TYPE);
uint8_t sequence_number = 0;

void colorWipe(uint32_t c) {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
  }
  strip.show();
}

void setup() {
  pinMode(PIXEL_PIN, OUTPUT);

  Udp.setBuffer(1500);
  Udp.begin(UDP_PORT);

  Serial.begin(9600);
  delay(1000); //to give the serial port time to open

  IPAddress ip = WiFi.localIP();
  Serial.printlnf("Connected to %s, listening at %d.%d.%d.%d:%d", WiFi.SSID(), ip[0], ip[1], ip[2], ip[3], UDP_PORT);
  strip.setBrightness(30);

  strip.begin();
  strip.show();
  colorWipe(strip.Color(0xFF, 0xE6, 0x9B));
}

char data[MAX_PACKET_SIZE];
unsigned long bytes;
int voxelIdx = 0;

void debug(String message) {
  #ifdef ENABLE_DEBUG
  Serial.printlnf(message);
  #endif
}

void udp_cleanup(){
  // Ignore other chars
  Udp.flush();
}

void loop() {
  bytes = Udp.parsePacket();
  if (bytes > 0) {
    memset(data, '\0', sizeof(char)*MAX_PACKET_SIZE);

    Udp.read(data, bytes);

    // Check for handshake control value
    if (data[0] == 0) {
      // Seed sequence number
      sequence_number = data[1];
      udp_cleanup();
      return;
    }
    // Before proceeding, verify the packet is not outdated
    else if (sequence_number > data[1]) {
      // Cheap hack to let us workaround dropped packets during a sequence number wraparound
      // Handles the event a few packets are out of order, but can result in desynchronization if large amounts of packets are lost or delivered out of order
      if (data[1] == 0 || 256 - data[1] > 128) {
        sequence_number = data[1];
        debug(String::format("Detected wraparound on sequence number, new value=%d", sequence_number));
      }
      else {
        debug("Ignoring out of order packet");
        udp_cleanup();
        return;
      }
    }
    else {
      // Packet is newer than last received packet (but not necessarily sequential)
      sequence_number = data[1];
    }

    // Check control code to take appropriate action
    if (data[0] == 1) {
      // Set pixel colors
      uint16_t start = (data[2] << 8) + data[3];
      uint8_t r = 0;
      uint8_t g = 0;
      uint8_t b = 0;
      int idx = 4;
      int offset = 0;
      while (idx < bytes) {
        r = data[idx];
        g = data[idx+1];
        b = data[idx+2];
        //Serial.printlnf("Setting pixel %d to RGB %d %d %d", start + offset, r, g, b);
        strip.setPixelColor(start + offset, strip.Color(r, g, b));
        idx += 3;
        offset += 1;

        if (start + offset > PIXEL_CNT) {
          debug(String::format("Exiting because offset (%d) should never be higher than the pixel count (%d).", start + offset, PIXEL_CNT));
          break;
        }
      }
    }
    else if (data[0] == 2) {
      // Refresh pixels at once
      strip.show();
    }
    else {
      // Invalid packet, disregard
      debug("Ignoring malformed packet");
    }

    udp_cleanup();
  }
}
