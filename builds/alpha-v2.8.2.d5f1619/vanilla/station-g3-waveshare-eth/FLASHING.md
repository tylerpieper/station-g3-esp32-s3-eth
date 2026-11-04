# Flashing Guide: Station G3 (Waveshare ESP32-S3-ETH) — v2.8.2.d5f1619

This package includes the complete 16 MB partition layout for the **Station G3 + Waveshare ESP32-S3-ETH Interposer**, including the custom **W5500 Wired Ethernet + BLE OTA Bootloader** (`mt-esp32s3-ota.bin` at `app1` / `0x650000`).

---

## 16 MB Flash Partition Layout (`default_16MB.csv`)

| Partition | Offset | Size | Binary File | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bootloader` / `partitions` / `boot_app0` / `app0` | `0x000000` | `~2.4 MB` | `firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin` | Bootloader, Partition Table, and Primary Meshtastic Firmware (`app0` @ `0x010000`) |
| `app1` (`ota_1`) | `0x650000` | `6.25 MB` | `mt-esp32s3-ota.bin` | Dedicated **W5500 Ethernet + BLE Unified OTA Bootloader** |
| `spiffs` | `0xC90000` | `3.375 MB` | `littlefs-station-g3-waveshare-eth-2.8.2.d5f1619.bin` | LittleFS Web UI & Filesystem |
| **Combined Full Image** | `0x000000` | `~16 MB` | `firmware-station-g3-waveshare-eth-2.8.2.d5f1619.full.bin` | All-in-one merged image (`0x0` + `0x650000` + `0xC90000`) |

---

## Option A: Automated Full Flash via Script (Recommended for Initial Install)

Flashes `factory.bin` (`0x0`), `mt-esp32s3-ota.bin` (`0x650000`), and `littlefs.bin` (`0xC90000`) automatically.

### Prerequisites
* Python 3 with `esptool` installed (`pip install esptool`)
* Put the Waveshare ESP32-S3-ETH into USB bootloader mode (hold **BOOT**, tap **RESET**, release **BOOT**).

### Linux / macOS
```bash
./device-install.sh -p /dev/ttyACM0 -f firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin
```

### Windows (PowerShell / CMD)
```powershell
.\device-install.bat -p COM3 -f firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin
```

---

## Option B: Single-File Full Flash (Web Flasher or `esptool` All-in-One)

If using a single-file flasher (such as ESP Web Tools, Espressif Flash Download Tool, or single-command `esptool`), flash the `.full.bin` image at offset `0x0`:

```bash
python -m esptool --chip esp32s3 --port <PORT> erase-flash
python -m esptool --chip esp32s3 --port <PORT> write-flash 0x0 firmware-station-g3-waveshare-eth-2.8.2.d5f1619.full.bin
```

---

## Option C: Manual Multi-Partition Flash (`esptool`)

```bash
python -m esptool --chip esp32s3 --port <PORT> erase-flash
python -m esptool --chip esp32s3 --port <PORT> write-flash \
  0x000000 firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin \
  0x650000 mt-esp32s3-ota.bin \
  0xC90000 littlefs-station-g3-waveshare-eth-2.8.2.d5f1619.bin
```

---

## Option D: Wired Ethernet OTA Update (No USB Required)

Once the device has been flashed with this setup (which installs `mt-esp32s3-ota.bin` in `app1`), future updates can be performed directly over **Wired Ethernet (TCP port 3232)** for both **DHCP** and **Static IP** configurations:

```bash
# Using Meshtastic Python CLI (>= 2.5+):
meshtastic --host <DEVICE_IP> --ota-update firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin
```

---

## Option E: USB Firmware Update (Preserves Settings)

To update only the `app0` firmware (`0x10000`) over USB without erasing NVS configuration or LittleFS:

```bash
# Linux / macOS:
./device-update.sh -p /dev/ttyACM0 -f firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin

# Windows:
.\device-update.bat -p COM3 -f firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin
```
