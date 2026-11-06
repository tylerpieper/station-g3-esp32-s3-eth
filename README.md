# Station G3 — Waveshare ESP32-S3-ETH Custom Hardware & Firmware

[![Build & Release Pipeline](https://github.com/tylerpieper/station-g3-esp32-s3-eth/actions/workflows/build-pipeline.yml/badge.svg)](https://github.com/tylerpieper/station-g3-esp32-s3-eth/actions/workflows/build-pipeline.yml)

Hardware design (KiCad interposer) and automated Meshtastic firmware builds for the **B&Q Consulting Station G3** baseboard paired with the **Waveshare ESP32-S3-ETH** (W5500 Wired Ethernet + PoE) module.

Each release automatically compiles upstream [Meshtastic Firmware](https://github.com/meshtastic/firmware) and integrates the custom **Wired Ethernet + BLE Unified OTA Bootloader** from [`tylerpieper/meshtastic-esp32-ethernet-ota`](https://github.com/tylerpieper/meshtastic-esp32-ethernet-ota) into the `app1` (`0x650000`) partition.

---

## Key Features

* **Station G3 High-Power RF Baseboard**: Full support for the primary slot `BQ35LORA900V1M` SX1262 LoRa module (`SX126X_MAX_POWER=19` -> ~31 dBm at PA `PL1`), INA219 telemetry/EEPROM I2C bus, SH1107 128x64 Grove OLED, and Grove UART GPS.
* **Native W5500 10/100Mbps Ethernet (`SPI3_HOST`)**: Dedicated high-speed SPI bus (`GPIO 9..14`) for wired Ethernet + UDP Multicast (`HAS_UDP_MULTICAST=1`) without contending with the LoRa `SPI2_HOST` bus.
* **Full Wired Ethernet + BLE OTA Support (`app1` @ `0x650000`)**:
  * Integrates [`tylerpieper/meshtastic-esp32-ethernet-ota`](https://github.com/tylerpieper/meshtastic-esp32-ethernet-ota) directly into the 16 MB partition layout (`mt-esp32s3-ota.bin`).
  * Includes [`patches/station-g3-eth-ota.patch`](patches/station-g3-eth-ota.patch) so both **DHCP** and **Static IP** configurations (`static_ip`, `static_gw`, `static_mask`, `static_dns`, `eth_enabled`) are seamlessly handed off via NVS to the OTA bootloader and recovered after update.
  * Preserves the ESP32 factory Ethernet MAC address (`ESP_MAC_ETH`) between `app0` and `app1` so DHCP servers assign the exact same IP address during OTA updates.
* **Automated Upstream Tracking & GitHub Releases**:
  * Polls [`meshtastic/firmware`](https://github.com/meshtastic/firmware) every 6 hours and publishes ready-to-flash release bundles on the [GitHub Releases](https://github.com/tylerpieper/station-g3-esp32-s3-eth/releases) page and in [`./builds/INDEX.md`](builds/INDEX.md).

---

## 16 MB Flash Partition Table (`default_16MB.csv`)

| Partition | Flash Offset | Size | Binary Artifact | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `bootloader` / `partitions` / `boot_app0` | `0x000000` | `64 KB` | *(Inside `.factory.bin` & `.full.bin`)* | Second-stage bootloader, partition table, and OTA data selector |
| `app0` (`ota_0`) | `0x010000` | `6.25 MB` | `firmware-station-g3-waveshare-eth-<ver>.bin` | Primary Meshtastic Firmware (`app0`) |
| `app1` (`ota_1`) | `0x650000` | `6.25 MB` | `mt-esp32s3-ota.bin` | **W5500 Ethernet + BLE Unified OTA Bootloader** ([`meshtastic-esp32-ethernet-ota`](https://github.com/tylerpieper/meshtastic-esp32-ethernet-ota)) |
| `spiffs` | `0xC90000` | `3.375 MB` | `littlefs-station-g3-waveshare-eth-<ver>.bin` | LittleFS Web UI & Filesystem |
| **Combined Full Image** | `0x000000` | `~16 MB` | `firmware-station-g3-waveshare-eth-<ver>.full.bin` | Single-file image with `0x0`, `0x650000` (`app1`), and `0xC90000` (`spiffs`) pre-merged |

---

## Flashing Instructions

### Option 1: Web Flasher (Recommended — No CLI or Tools Required)

You can flash directly from any WebSerial-compatible browser (Google Chrome, Microsoft Edge, Opera, Brave) using our **Custom Meshtastic Web Flasher**:

👉 **[Launch Custom Meshtastic Web Flasher](https://tylerpieper.github.io/Meshtastic-custom-web-flasher/)**

1. Connect the Waveshare ESP32-S3-ETH module to your computer via USB-C.
2. Put the board into bootloader mode: hold down **BOOT**, tap **RESET**, then release **BOOT**.
3. On the Web Flasher, click **Select Device** and choose **Station G3 (Waveshare ESP32-S3-ETH)**.
4. Select the release channel (**Alpha** or **Beta/Stable**) and firmware version.
5. Click **Flash Device** (leave *Full Erase and Install* selected on initial installation so all partitions, including LittleFS and the W5500 Ethernet OTA bootloader, are installed).

---

### Option 2: Command-Line Flashing (Local Tools)

Download the latest release package from the [**GitHub Releases**](https://github.com/tylerpieper/station-g3-esp32-s3-eth/releases) page (`station-g3-waveshare-eth-<version>-vanilla-full-package.zip`) or grab the `.full.bin` directly from [`builds/`](builds/INDEX.md).

#### Initial Full Flash (Erases Flash & Installs All Partitions)

Put the Waveshare ESP32-S3-ETH into USB bootloader mode (hold **BOOT**, tap **RESET**, release **BOOT**).

##### Method A: Automated Script (Recommended)
```bash
# Linux / macOS:
./device-install.sh -p /dev/ttyACM0 -f firmware-station-g3-waveshare-eth-<version>.factory.bin

# Windows (PowerShell / CMD):
.\device-install.bat -p COM3 -f firmware-station-g3-waveshare-eth-<version>.factory.bin
```

##### Method B: Single-File All-in-One Merged Flash (`.full.bin`)
Flash the single pre-merged 16 MB binary at offset `0x0`:
```bash
python -m esptool --chip esp32s3 --port <PORT> erase-flash
python -m esptool --chip esp32s3 --port <PORT> write-flash 0x0 firmware-station-g3-waveshare-eth-<version>.full.bin
```

##### Method C: Manual Multi-Partition `esptool` Flash
```bash
python -m esptool --chip esp32s3 --port <PORT> erase-flash
python -m esptool --chip esp32s3 --port <PORT> write-flash \
  0x000000 firmware-station-g3-waveshare-eth-<version>.factory.bin \
  0x650000 mt-esp32s3-ota.bin \
  0xC90000 littlefs-station-g3-waveshare-eth-<version>.bin
```

---

### 2. Subsequent Firmware Updates (Preserves Settings)

#### Over Wired Ethernet (OTA — No USB Required)
Once `mt-esp32s3-ota.bin` is installed in `app1` (`0x650000`), you can update the node remotely over Ethernet (TCP port `3232`) using the Meshtastic CLI:
```bash
meshtastic --host <DEVICE_IP> --ota-update firmware-station-g3-waveshare-eth-<version>.bin
```

#### Over USB Serial (`device-update`)
```bash
# Linux / macOS:
./device-update.sh -p /dev/ttyACM0 -f firmware-station-g3-waveshare-eth-<version>.bin

# Windows:
.\device-update.bat -p COM3 -f firmware-station-g3-waveshare-eth-<version>.bin
```

---

## Repository Structure

* [`hardware/`](hardware/README.md) — KiCad schematic, PCB layout, BOM, and fabrication files for the Station G3 Waveshare ESP32-S3-ETH interposer.
* [`variants/esp32s3/station-g3-waveshare-eth/`](variants/esp32s3/station-g3-waveshare-eth/) — Custom PlatformIO environment, pin definitions, and fallback `mt-esp32s3-ota.bin`.
* [`patches/`](patches/) — Firmware patches including [`station-g3-eth-ota.patch`](patches/station-g3-eth-ota.patch) for Static IP + Ethernet NVS OTA handoff.
* [`build-config.yaml`](build-config.yaml) — Release channel tracking and build profile configuration.
* [`builds/`](builds/INDEX.md) — Automatically maintained index and artifacts for active Alpha and Beta releases.
