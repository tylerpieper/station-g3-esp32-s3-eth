#ifndef Pins_Arduino_h
#define Pins_Arduino_h

#include <stdint.h>

#define USB_VID 0x303a
#define USB_PID 0x1001

// The default Wire will be mapped to Screen and Sensors
static const uint8_t SDA = 40;
static const uint8_t SCL = 41;

// Default SPI will be mapped to Primary LoRa Radio
static const uint8_t SS = 2;
static const uint8_t MOSI = 15;
static const uint8_t MISO = 1;
static const uint8_t SCK = 3;

#endif /* Pins_Arduino_h */
