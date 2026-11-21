# Station G3 — Stock MCU to Waveshare ESP32-S3-ETH Migration Guide

This guide walks you through migrating an existing **B&Q Consulting Station G3** from its stock `BQESP32V1M` MCU daughterboard to the **Waveshare ESP32-S3-ETH** (W5500 Wired Ethernet + PoE) module using the custom interposer board, while preserving your existing node identity, channels, keys, and configurations.

---

> [!CAUTION]
> **RF Power Amplifier Safety Warning**  
> The Station G3 features a high-power RF stage (up to +31 to +35 dBm). **NEVER power up the Station G3 baseboard without a tuned antenna or a 50Ω dummy load attached to the primary RF port.** Operating the PA into an open load can permanently damage the SX1262 power amplifier stage within seconds.

---

## Migration Overview & Checklist

| Step | Task | Description |
| :--- | :--- | :--- |
| **1** | **Set Bluetooth to Fixed PIN** | Locks in a known 6-digit pairing PIN so you can connect to the headless Waveshare module. |
| **2** | **Disable Wi-Fi** | Ensures Bluetooth stays active without radio conflicts or Wi-Fi auto-shutdown. |
| **3** | **Export Config Backup** | Backs up node identity, radio settings, and channels to your phone or PC. |
| **4** | **Flash & Restore Standalone** | Flashes the Waveshare board over USB on your bench and restores the backup over BLE. |
| **5** | **Install Hardware** | Mounts the Waveshare module onto the interposer and seats it into the Station G3 baseboard. |
| **6** | **Enable Ethernet** | Boots up the Station G3, connects via BLE, enables wired Ethernet, and configures IP mode. |

---

## Step-by-Step Procedure

### Step 1: Set Bluetooth to "Fixed PIN"

The stock Station G3 daughterboard has an OLED screen to display random Bluetooth pairing PINs, but the standalone Waveshare ESP32-S3-ETH module is headless on your bench before installation. Setting a Fixed PIN ensures you can pair with it immediately upon initial boot.

1. Connect to your stock Station G3 using the **Meshtastic App** (Android, iOS, or Web/Desktop).
2. Open **Radio Configuration** &rarr; **Bluetooth Config**.
3. Set **Mode** to `Fixed PIN`.
4. Enter a 6-digit PIN that you know (e.g., `123456`).
5. Tap **Send** / **Save**. The node will reboot and use this fixed PIN for all future Bluetooth pairings.

---

### Step 2: Disable Wi-Fi on the Stock G3

On ESP32 architectures, running Wi-Fi and Bluetooth simultaneously can cause radio contention, and Meshtastic disables or deprioritizes BLE when Wi-Fi is actively connected. Disabling Wi-Fi guarantees Bluetooth connectivity remains stable during the backup and restore process.

1. In the Meshtastic App, open **Radio Configuration** &rarr; **Network Config**.
2. Toggle **Wi-Fi Enabled** to `OFF` (or clear the SSID/password).
3. Save changes. The node will reboot with Wi-Fi disabled and Bluetooth active.

---

### Step 3: Connect via Bluetooth and Export Configuration Backup

1. Pair your phone or PC with the Station G3 over Bluetooth using the Fixed PIN set in Step 1.
2. In the Meshtastic App:
   * **Android / iOS**: Open **Settings** / **Radio Configuration** &rarr; select **Export Backup** (or **Share Configuration** / **Device Profile**).
   * Save the backup file (`.yaml` / `.json`) or export string to your device.
3. *(Optional CLI Method)*: If connected over USB or serial:
   ```bash
   meshtastic --export-config > station-g3-backup.yaml
   ```
4. Verify that the backup includes your channels, node name, LoRa configuration, and user settings.

---

### Step 4: Flash the Waveshare Board & Restore Backup (Standalone)

Perform this step on your workbench **before** installing the board into the Station G3 baseboard.

1. Connect the Waveshare ESP32-S3-ETH module directly to your computer using a USB-C cable.
2. Put the board into bootloader mode:
   * Press and hold the **BOOT** button (GPIO0).
   * Tap the **RESET** button.
   * Release the **BOOT** button.
3. Flash the firmware using either option:
   * **Option A — Custom Web Flasher (Recommended)**:
     1. Open the [Custom Meshtastic Web Flasher](https://tylerpieper.github.io/Meshtastic-custom-web-flasher/).
     2. Select **Station G3 (Waveshare ESP32-S3-ETH)**.
     3. Select the desired release channel (**Alpha** or **Beta/Stable**).
     4. Click **Flash Device** (ensure *Full Erase and Install* is selected to flash `app0`, the W5500 Ethernet OTA bootloader in `app1`, and LittleFS).
   * **Option B — Local Installation Script**:
     ```powershell
     # Windows PowerShell
     .\device-install.bat -p COMx -f firmware-station-g3-waveshare-eth-<version>.factory.bin
     ```
     ```bash
     # Linux / macOS
     ./device-install.sh -p /dev/ttyACM0 -f firmware-station-g3-waveshare-eth-<version>.factory.bin
     ```
4. Once flashing completes, power-cycle the Waveshare module (unplug and replug the USB-C cable to standard USB power).
5. Open your Meshtastic App and search for Bluetooth devices.
6. Connect to the newly flashed Waveshare node using the **Fixed PIN** configured in Step 1.
7. Restore your configuration backup:
   * In the Meshtastic App, navigate to **Settings** / **Radio Configuration** &rarr; select **Restore Backup** (or **Import Device Profile**).
   * Select the backup saved in Step 3 and apply changes.
   * Node will reboot with your restored node identity and channels.

---

### Step 5: Power Down, Unplug, and Install into the Station G3

1. Unplug the USB-C cable from the Waveshare ESP32-S3-ETH module.
2. Power off the Station G3 baseboard and disconnect all external power (USB-C PD or DC barrel jack).
3. Carefully remove the stock `BQESP32V1M` daughterboard from the Station G3 40-pin header (`J1`).
4. Mount the Waveshare ESP32-S3-ETH module onto the **Station G3 Ethernet Interposer PCB**.
5. Plug the interposer assembly firmly into the Station G3 40-pin baseboard socket (`J1`).
   * *Verify pin 1 orientation and ensure all 40 pins seat straight without bending.*
6. **Double-check RF Connection**: Ensure your antenna or 50Ω dummy load is securely threaded onto the baseboard's primary SMA / N-type RF connector.

---

### Step 6: Power Up G3, Connect via Bluetooth, and Enable Ethernet

1. Connect main power to the Station G3 baseboard (USB-C PD 15V or DC barrel jack 9V–19V).
2. The onboard Grove OLED display (SH1107 128x64) will turn on and show the Meshtastic logo and status screens.
3. Open the Meshtastic App on your phone/PC and connect via Bluetooth (using your Fixed PIN).
4. Configure Ethernet:
   * Open **Radio Configuration** &rarr; **Network Config**.
   * Toggle **Ethernet Enabled** (`eth_enabled`) to `ON`.
   * **Address Mode**:
     * **DHCP** *(Default)*: The node will automatically acquire an IP, gateway, and DNS from your network router.
     * **Static IP**: If you require a static IP, set **Address Mode** to `STATIC` and enter your IP, Gateway, Subnet Mask, and DNS server.
   * Tap **Send** / **Save**.
5. Plug your Ethernet cable (RJ45) into the Waveshare ESP32-S3-ETH jack (PoE or non-PoE network switch).
6. The node will reboot and initialize the onboard W5500 Ethernet controller (`SPI3_HOST`).
7. Check the OLED screen or your router's DHCP lease table to confirm the node has connected and displays its IP address (e.g., `10.1.1.130`).

---

## Post-Migration Features & Tips

### Remote Ethernet OTA Updates (No USB Required)
With the custom Ethernet firmware installed, `app1` contains the dedicated W5500 Ethernet OTA bootloader. You no longer need to connect via USB for future firmware updates:
```bash
meshtastic --host <DEVICE_IP> --ota-update firmware-station-g3-waveshare-eth-<version>.bin
```
The update will stream over Ethernet at ~100–150 KB/s, verify the SHA-256 hash, and reboot automatically into the new firmware while preserving all configuration settings and static/DHCP IP assignments.

### Optional: Returning Bluetooth to Random PIN
Now that the Grove OLED screen is connected and functional through the G3 baseboard, you can safely return Bluetooth to **Random PIN** mode if desired:
1. Open **Radio Configuration** &rarr; **Bluetooth Config**.
2. Change **Mode** from `Fixed PIN` to `Random PIN`.
3. Save changes. Future pairing codes will be displayed directly on the Station G3 OLED screen.
