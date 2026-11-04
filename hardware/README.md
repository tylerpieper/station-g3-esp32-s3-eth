# Hardware Design Files (KiCad) — Station G3 Waveshare ESP32-S3-ETH Interposer

This directory is dedicated to the hardware design files for the **Station G3 + Waveshare ESP32-S3-ETH Custom Interposer**.

## Recommended Directory Layout

* `kicad/` — KiCad project (`.kicad_pro`), schematic (`.kicad_sch`), and PCB layout (`.kicad_pcb`)
* `gerbers/` — Fabrication Gerber & drill archives (`.zip`)
* `bom/` — Bill of Materials (`.csv` / `.xlsx`) and interactive BOM (`.html`)
* `3d/` — STEP / STL enclosure and mechanical fitment models

## Interposer Pin Mapping Summary

| Function | Station G3 Baseboard Header (`J1`) | Waveshare ESP32-S3-ETH Pin | Notes |
| :--- | :--- | :--- | :--- |
| **I2C SDA** (OLED / INA219 / EEPROM) | `J1` Pins 3 & 27 | `GPIO 40` (`J2` Pin 11) | `USE_SH1107_128_64` |
| **I2C SCL** (OLED / INA219 / EEPROM) | `J1` Pins 5 & 28 | `GPIO 41` (`J2` Pin 10) | |
| **GPS / Grove UART TX** | `J1` Pin 8 | `GPIO 48` (`J2` Pin 4) | `HAS_GPS=1` |
| **GPS / Grove UART RX** | `J1` Pin 10 | `GPIO 47` (`J2` Pin 5) | |
| **LoRa MISO** (`BQ35LORA900V1M` SX1262) | `J1` Pin 21 | `GPIO 1` (`J3` Pin 25) | `SPI2_HOST` |
| **LoRa CS (NSS)** | `J1` Pin 24 | `GPIO 2` (`J3` Pin 26) | |
| **LoRa SCK** | `J1` Pin 23 | `GPIO 3` (`J3` Pin 27) | |
| **LoRa MOSI** | `J1` Pin 19 | `GPIO 15` (`J3` Pin 29) | |
| **LoRa RESET** | `J1` Pin 36 | `GPIO 39` (`J2` Pin 12) | |
| **LoRa DIO1** | `J1` Pin 15 | `GPIO 17` (`J3` Pin 34) | |
| **LoRa BUSY** | `J1` Pin 18 | `GPIO 18` (`J3` Pin 31) | |
| **LoRa PA Mode** | `J1` Pin 11 | `GPIO 42` (`J2` Pin 9) | Controlled by jumper `PA-PL1/PL2` by default |
| **LoRa LNA Mode** | `J1` Pin 16 | `GPIO 16` (`J3` Pin 32) | Controlled by jumper `LNA-P` by default |
| **W5500 Ethernet MOSI** | *(Onboard Waveshare)* | `GPIO 11` | `SPI3_HOST` |
| **W5500 Ethernet MISO** | *(Onboard Waveshare)* | `GPIO 12` | |
| **W5500 Ethernet SCLK** | *(Onboard Waveshare)* | `GPIO 13` | |
| **W5500 Ethernet CS** | *(Onboard Waveshare)* | `GPIO 14` | |
| **W5500 Ethernet INT** | *(Onboard Waveshare)* | `GPIO 10` | |
| **W5500 Ethernet RST** | *(Onboard Waveshare)* | `GPIO 9` | |
| **User Button (BOOT)** | *(Onboard Waveshare)* | `GPIO 0` | Active LOW with internal pull-up |
| **Status RGB LED (WS2812)** | *(Onboard Waveshare)* | `GPIO 21` | `HAS_NEOPIXEL=1` |
