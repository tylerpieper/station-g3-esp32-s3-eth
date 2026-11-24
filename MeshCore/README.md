# MeshCore for Station G3 + Waveshare ESP32-S3-ETH

This directory contains the self-contained **MeshCore** variant definition and pre-built merged binaries for running [MeshCore](https://github.com/meshcore-dev/MeshCore) on the **B&Q Consulting Station G3** baseboard with the **Waveshare ESP32-S3-ETH** module and custom interposer PCB.

> [!CAUTION]
> **RF Power Amplifier Safety Warning**  
> The Station G3 includes a high-power RF stage (up to +31 to +35 dBm). **NEVER power on the Station G3 baseboard without a properly tuned antenna or 50Ω dummy load attached to the primary RF connector.** Transmitting into an open load can permanently damage the power amplifier.

> [!NOTE]
> **Ethernet & OTA Scope**  
> This variant is designed to get MeshCore running cleanly on the Station G3 + Waveshare ESP32-S3-ETH hardware without modifying MeshCore core files. Wired W5500 Ethernet and custom Ethernet OTA are **not** included in MeshCore (upstream MeshCore currently supports BLE, USB Serial, and Wi-Fi on ESP32-S3).

---

## Pre-Built Binaries (`v1.18.0`)

Pre-built, single-file merged images (`*-merged.bin`, ready to flash at offset `0x0`) for MeshCore **v1.18.0** (commit `81dbae59`) are located in [`binaries/v1.18.0/`](binaries/v1.18.0/):

| Binary | Role | Notes |
| :--- | :--- | :--- |
| `Station_G3_Waveshare_ETH_repeater-v1.18.0-merged.bin` | **Repeater** | Standalone LoRa repeater with OLED UI & FEM control |
| `Station_G3_Waveshare_ETH_room_server-v1.18.0-merged.bin` | **Room Server** | MeshCore BBS / chat room server |
| `Station_G3_Waveshare_ETH_companion_radio_ble-v1.18.0-merged.bin` | **Companion (BLE)** | Bluetooth companion radio for the MeshCore mobile app (default PIN: `123456`) |
| `Station_G3_Waveshare_ETH_companion_radio_usb-v1.18.0-merged.bin` | **Companion (USB)** | USB Serial companion radio for desktop/web clients |
| `Station_G3_Waveshare_ETH_companion_radio_wifi-v1.18.0-merged.bin` | **Companion (Wi-Fi)** | Wi-Fi companion radio *(requires editing `WIFI_SSID` / `WIFI_PWD` and building from source for your network)* |
| `Station_G3_Waveshare_ETH_kiss_modem-v1.18.0-merged.bin` | **KISS Modem** | KISS TNC modem over USB |

---

## Flashing a Pre-Built Binary (No Build Tools Required)

You can flash any `*-merged.bin` file directly to the Waveshare ESP32-S3-ETH over USB-C before (or after) installing it onto the Station G3 interposer.

### 1. Enter USB Bootloader Mode
1. Connect the Waveshare ESP32-S3-ETH to your computer via USB-C.
2. Hold down the **BOOT** button, tap the **RESET** button, then release **BOOT**.

### 2. Flash to Offset `0x0`
* **Option A — Browser (Easiest, no installs)**:
  1. Open [ESP Web Tool (Adafruit / Espressif ESPTool JS)](https://espressif.github.io/esptool-js/) in Chrome or Edge.
  2. Click **Connect** and select your ESP32-S3 serial port.
  3. *(Optional)* Click **Erase Flash** for a clean install.
  4. Set **Flash Address** to `0x0`, select your chosen `*-merged.bin` file, and click **Program**.
  5. Unplug/replug USB (or tap **RESET**) to boot into MeshCore.
* **Option B — Command Line (`esptool`)**:
  ```bash
  # Install esptool once (requires Python 3):
  pip install esptool

  # Erase and flash (replace COMx or /dev/ttyACM0 with your port):
  python -m esptool --chip esp32s3 --port COMx erase-flash
  python -m esptool --chip esp32s3 --port COMx write-flash 0x0 binaries/v1.18.0/Station_G3_Waveshare_ETH_repeater-v1.18.0-merged.bin
  ```

---

## Building from Source (Step-by-Step)

If you want to customize settings (such as Wi-Fi credentials, repeater name/password, or building against a newer MeshCore release), you only need to drop our variant folder into a standard MeshCore checkout.

### Prerequisites
1. Install **[Git](https://git-scm.com/downloads)**.
2. Install **[Visual Studio Code](https://code.visualstudio.com/)** and the **[PlatformIO IDE](https://platformio.org/install/ide?install=vscode)** extension (or install the [PlatformIO Core CLI](https://docs.platformio.org/en/latest/core/installation/index.html) directly).
   * Official MeshCore build documentation: [MeshCore README & Docs](https://github.com/meshcore-dev/MeshCore)

### Step 1: Clone MeshCore
```bash
git clone https://github.com/meshcore-dev/MeshCore.git
cd MeshCore
```
*(Optional)* Check out a specific release tag (for example, `v1.18.0`):
```bash
git checkout companion-v1.18.0
```

### Step 2: Copy the Variant Definition
Copy the entire [`variants/station_g3_waveshare_eth/`](variants/station_g3_waveshare_eth/) folder from this repository into `MeshCore/variants/`:
```text
MeshCore/
└── variants/
    └── station_g3_waveshare_eth/
        ├── LoRaFEMControl.cpp
        ├── LoRaFEMControl.h
        ├── platformio.ini
        ├── StationG3Board.cpp
        ├── StationG3Board.h
        ├── target.cpp
        └── target.h
```
MeshCore's root `platformio.ini` automatically discovers all `variants/*/platformio.ini` files — no other files need to be edited.

### Step 3: *(Optional)* Customize Build Flags
Open `variants/station_g3_waveshare_eth/platformio.ini` to adjust:
* **Wi-Fi credentials** (for `Station_G3_Waveshare_ETH_companion_radio_wifi`): `WIFI_SSID` and `WIFI_PWD`
* **BLE PIN** (for `Station_G3_Waveshare_ETH_companion_radio_ble`): `BLE_PIN_CODE`
* **Repeater / Room defaults**: `ADVERT_NAME`, `ADMIN_PASSWORD`, `ROOM_PASSWORD`

### Step 4: Build & Flash
Using the **PlatformIO CLI** (or the PlatformIO sidebar in VS Code):

```bash
# Build a specific role (e.g. repeater):
pio run -e Station_G3_Waveshare_ETH_repeater

# Build a single-file merged binary (output: .pio/build/<env>/firmware-merged.bin):
pio run -e Station_G3_Waveshare_ETH_repeater -t mergebin

# Build and flash directly over USB (put board in BOOT mode first):
pio run -e Station_G3_Waveshare_ETH_repeater -t upload --upload-port COMx
```

---

## Hardware Pin Mapping Summary

The variant matches the Rev 1.0 Station G3 + Waveshare ESP32-S3-ETH interposer schematic:

| Function | ESP32-S3 GPIO | Interposer / Baseboard Signal |
| :--- | :---: | :--- |
| LoRa MISO | `GPIO1` | J3 Pin 25 &larr; J1 Pin 21 (Primary Slot MISO) |
| LoRa NSS (CS) | `GPIO2` | J3 Pin 26 &larr; J1 Pin 24 (Primary Slot NSS) |
| LoRa SCK | `GPIO3` | J3 Pin 27 &larr; J1 Pin 23 (Primary Slot SCK) |
| LoRa MOSI | `GPIO15` | J3 Pin 29 &larr; J1 Pin 19 (Primary Slot MOSI) |
| LoRa DIO1 | `GPIO17` | J3 Pin 34 &larr; J1 Pin 15 (Primary Slot DIO1) |
| LoRa BUSY | `GPIO18` | J3 Pin 31 &larr; J1 Pin 18 (Primary Slot BUSY) |
| LoRa RESET | `GPIO39` | J2 Pin 12 &larr; J1 Pin 36 (Primary Slot NRESET) |
| PA Mode (`P_PA1_EN`) | `GPIO42` | J2 Pin 9 &larr; J1 Pin 11 (Active `HIGH`) |
| LNA Mode (`P_PRIMARY_LNA_EN`) | `GPIO16` | J3 Pin 32 &larr; J1 Pin 16 (Active `LOW`) |
| I2C SDA (OLED / INA219) | `GPIO40` | J2 Pin 11 &larr; J1 Pins 3 & 27 |
| I2C SCL (OLED / INA219) | `GPIO41` | J2 Pin 10 &larr; J1 Pins 5 & 28 |
| Grove GPS TX (MCU RX) | `GPIO47` | J2 Pin 5 &larr; J1 Pin 10 |
| Grove GPS RX (MCU TX) | `GPIO48` | J2 Pin 4 &larr; J1 Pin 8 |
| User Button | `GPIO0` | Waveshare onboard BOOT button |

* `LORA_TX_POWER=7` dBm default / `MAX_LORA_TX_POWER=19` dBm cap (ISM-compliant PA Level 1 limit).
* Software FEM CLI controls (`get/set radio.fem.rxgain` and `get/set radio.fem.txgain`) are supported when the corresponding hardware jumpers are removed.
