#pragma once

// ============================================================================
// Station G3 + Waveshare ESP32-S3-ETH Custom Interposer (Rev 1.0)
// ============================================================================

// 1. I2C Bus (Grove OLED + Station G3 INA219/EEPROM on J1 Pins 3, 5, 27, 28)
#define USE_SH1107_128_64
#define I2C_SDA 40 // J2 Pin 11 (GPIO40) <- J1 Pins 3 & 27 (I2C SDA / EEPROM SDA)
#define I2C_SCL 41 // J2 Pin 10 (GPIO41) <- J1 Pins 5 & 28 (I2C SCL / EEPROM SCL)

// 2. Grove UART / GPS Header (J1 Pins 8 & 10)
#define HAS_GPS 1
#define GPS_TX_PIN 48 // J2 Pin 4 (GPIO48) <- J1 Pin 8  (UART TX)
#define GPS_RX_PIN 47 // J2 Pin 5 (GPIO47) <- J1 Pin 10 (UART RX)

// 3. User Button & Onboard WS2812 RGB Status LED (Waveshare ESP32-S3-ETH)
#define BUTTON_PIN 0 // Waveshare onboard BOOT button (GPIO0)
#define BUTTON_NEED_PULLUP

#define HAS_NEOPIXEL 1
#define NEOPIXEL_COUNT 1
#define NEOPIXEL_DATA 21 // Waveshare onboard WS2812 RGB LED (GPIO21)
#define NEOPIXEL_TYPE (NEO_GRB + NEO_KHZ800)

// 4. Station G3 Primary Slot SX1262 LoRa Radio (BQ35LORA900V1M)
#define USE_SX1262
#define LORA_MISO 1   // J3 Pin 25 (GPIO1)  <- J1 Pin 21 (Primary Slot MISO)
#define LORA_CS 2     // J3 Pin 26 (GPIO2)  <- J1 Pin 24 (Primary Slot NSS)
#define LORA_SCK 3    // J3 Pin 27 (GPIO3)  <- J1 Pin 23 (Primary Slot SCK)
#define LORA_MOSI 15  // J3 Pin 29 (GPIO15) <- J1 Pin 19 (Primary Slot MOSI)
#define LORA_RESET 39 // J2 Pin 12 (GPIO39) <- J1 Pin 36 (Primary Slot NRESET)
#define LORA_DIO1 17  // J3 Pin 34 (GPIO17) <- J1 Pin 15 (Primary Slot DIO1)

#ifdef USE_SX1262
#define SX126X_CS LORA_CS
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY 18 // J3 Pin 31 (GPIO18) <- J1 Pin 18 (Primary Slot BUSY)
#define SX126X_RESET LORA_RESET
#define SX126X_DIO2_AS_RF_SWITCH
#define SX126X_DIO3_TCXO_VOLTAGE 1.8

// Station G3 BQ35LORA900V1M PA cap (19 dBm SX1262 drive -> ~31 dBm out at PA PL1)
#define SX126X_MAX_POWER 19
#endif

// Station G3 Baseboard PA/LNA header pins (controlled by hardware jumpers PA-PL1/PL2 & LNA-P by default)
#define LORA_PA_MODE_PIN 42  // J2 Pin 9  (GPIO42) <- J1 Pin 11 (PA Mode)
#define LORA_LNA_MODE_PIN 16 // J3 Pin 32 (GPIO16) <- J1 Pin 16 (Primary Slot LNA Mode)

// 5. Waveshare Onboard W5500 10/100Mbps Ethernet (Internal SPI3_HOST Routing)
#define HAS_ETHERNET 1
#define USE_WS5500 1 // Uses ESP-IDF native W5500 driver in WiFiAPClient.cpp

#define ETH_MOSI_PIN 11
#define ETH_MISO_PIN 12
#define ETH_SCLK_PIN 13
#define ETH_CS_PIN 14
#define ETH_INT_PIN 10
#define ETH_RST_PIN 9
#define ETH_ADDR 1
