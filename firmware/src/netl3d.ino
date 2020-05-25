/**
 * Firmware to allow (relatively) efficient network control of an L3D cube
 */
#include "neopixel/neopixel.h"

#define ENABLE_DEBUG            true

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

// Gamma correction: https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix
// static const uint8_t gamma8[] = {
//     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
//     1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
//     2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
//     5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
//    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
//    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
//    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
//    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
//    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
//    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
//    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
//   115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
//   144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
//   177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
//   215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255
// };

// Gamma = 1.8: https://victornpb.github.io/gamma-table-generator/
static const uint8_t gamma8[] = {
     0,   0,   0,   0,   0,   0,   0,   0,   1,   1,   1,   1,   1,   1,   1,   2,
     2,   2,   2,   2,   3,   3,   3,   3,   4,   4,   4,   4,   5,   5,   5,   6,
     6,   6,   7,   7,   8,   8,   8,   9,   9,  10,  10,  10,  11,  11,  12,  12,
    13,  13,  14,  14,  15,  15,  16,  16,  17,  17,  18,  18,  19,  19,  20,  21,
    21,  22,  22,  23,  24,  24,  25,  26,  26,  27,  28,  28,  29,  30,  30,  31,
    32,  32,  33,  34,  35,  35,  36,  37,  38,  38,  39,  40,  41,  41,  42,  43,
    44,  45,  46,  46,  47,  48,  49,  50,  51,  52,  53,  53,  54,  55,  56,  57,
    58,  59,  60,  61,  62,  63,  64,  65,  66,  67,  68,  69,  70,  71,  72,  73,
    74,  75,  76,  77,  78,  79,  80,  81,  82,  83,  84,  86,  87,  88,  89,  90,
    91,  92,  93,  95,  96,  97,  98,  99, 100, 102, 103, 104, 105, 107, 108, 109,
   110, 111, 113, 114, 115, 116, 118, 119, 120, 122, 123, 124, 126, 127, 128, 129,
   131, 132, 134, 135, 136, 138, 139, 140, 142, 143, 145, 146, 147, 149, 150, 152,
   153, 154, 156, 157, 159, 160, 162, 163, 165, 166, 168, 169, 171, 172, 174, 175,
   177, 178, 180, 181, 183, 184, 186, 188, 189, 191, 192, 194, 195, 197, 199, 200,
   202, 204, 205, 207, 208, 210, 212, 213, 215, 217, 218, 220, 222, 224, 225, 227,
   229, 230, 232, 234, 236, 237, 239, 241, 243, 244, 246, 248, 250, 251, 253, 255,
};

// Enable logging via 'particle serial monitor'
//SerialLogHandler logHandler(115200, LOG_LEVEL_ALL);

UDP Udp;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(PIXEL_CNT, PIXEL_PIN, PIXEL_TYPE);
uint8_t sequence_number = 0;
// Global because referenced in variable later, do not want it unallocated from stack
String ip_str = "";
String ssid_str = "";
bool udp_needs_init = true;

void colorWipe(uint32_t c) {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
  }
  strip.show();
}

void setup() {
  Serial.begin(9600);
  delay(1000); //to give the serial port time to open

  debug("Entering setup sequence");

  pinMode(PIXEL_PIN, OUTPUT);

  WiFi.selectAntenna(ANT_AUTO);

  Serial.println("Known networks: ");
  WiFiAccessPoint ap[5];
  int network_count = WiFi.getCredentials(ap, 5);
  for (int i = 0; i < network_count; i++) {
    Serial.printlnf("%d. ssid=%s security=%s cipher=%s", i+1, ap[i].ssid, ap[i].security, ap[i].cipher);
  }

  IPAddress ip = WiFi.localIP();
  ip_str = String::format("%d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
  ssid_str = String(WiFi.SSID());
  Particle.variable("local_ip", ip_str);
  Particle.variable("ssid", ssid_str);
  Serial.printlnf("Connected to %s, listening at %d.%d.%d.%d:%d", ssid_str.c_str(), ip[0], ip[1], ip[2], ip[3], UDP_PORT);

  udp_setup();


  strip.begin();
  strip.setBrightness(30); // USB doesn't have power for all-white LEDs beyond this brightness
  colorWipe(strip.Color(gamma8[128], gamma8[110], gamma8[100]));
}

char data[MAX_PACKET_SIZE];
unsigned long bytes;
int voxelIdx = 0;

void debug(String message) {
  #if ENABLE_DEBUG
  Serial.printlnf(message);
  #endif
}

void udp_cleanup() {
  // Ignore other chars
  Udp.flush();
}

void udp_setup() {
  debug(String::format("Initializing UDP...", bytes));
  Udp.stop();
  Udp.setBuffer(1500);
  Udp.begin(UDP_PORT);
  udp_needs_init = false;
}

void loop() {
  bytes = Udp.parsePacket();
  if (!WiFi.ready()) {
    // We lost wifi and will need to manually reinitialize the socket until
    // this is fixed: https://github.com/particle-iot/firmware/pull/766
    debug(String::format("Lost wifi... waiting", bytes));
    udp_needs_init = true;
    delay(100);
    return;
  }
  if (udp_needs_init) {
    udp_setup();
  }

  if (bytes > 0) {
    debug(String::format("Received packet of %d bytes", bytes));
    memset(data, '\0', sizeof(char)*MAX_PACKET_SIZE);

    Udp.read(data, bytes);

    // Check for handshake control value
    if (data[0] == 0) {
      // Seed sequence number
      sequence_number = data[1];
      debug(String::format("Handshake detected: setting new sequence number=%d", data[1]));
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
      unsigned int idx = 4;
      int offset = 0;
      while (idx < bytes) {
        r = data[idx];
        g = data[idx+1];
        b = data[idx+2];
        //Serial.printlnf("Setting pixel %d to RGB %d %d %d", start + offset, r, g, b);
        strip.setPixelColor(start + offset, strip.Color(gamma8[r], gamma8[g], gamma8[b]));
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
  else {
    // I have a hunch without a delay, too busy processing UDP traffic and
    // cloud connection gets lost
    //delay(5);
  }
}
