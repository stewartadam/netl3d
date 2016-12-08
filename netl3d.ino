/**
 * Firmware to allow (relatively) efficient network control of an L3D cube
 */
#include "neopixel/neopixel.h"

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

void loop() {
  bytes = Udp.parsePacket();
  if (bytes > 0) {
    //Serial.printlnf("Read %d bytes.", bytes);
    memset(data, '\0', sizeof(char)*MAX_PACKET_SIZE);

    Udp.read(data, bytes);
    //for(int i = 0; i < MAX_PACKET_SIZE; i++)
    //  Serial.printf("%02X", data[i]);
    //Serial.println("");

    if (data[0] == 2) {
      strip.show();
    }
    else {
      uint16_t start = (data[0] << 8) + data[1];
      uint8_t r = 0;
      uint8_t g = 0;
      uint8_t b = 0;
      int idx = 2;
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
          Serial.println("Exiting because offset should never be higher than the pixel count.");
          break;
        }
      }
    }

    // Ignore other chars
    Udp.flush();
  }
}
