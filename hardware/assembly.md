# Interposer Board Assembly Guide — Station G3 <-> Waveshare ESP32-S3-ETH

This guide walks through hand-assembling the **Station G3 Waveshare ESP32-S3-ETH Interposer Board** (`31.5 mm × 65 mm` PCB).

Following the recommended soldering order (**`D1` -> `J1` -> `J2` & `J3`**) keeps tall header plastics out of the way while soldering surface-mount pads and tightly spaced through-hole rows.

---

## Parts & Tools Required

### Bill of Materials (per board, included when ordered from me)

| Ref | Qty | Component | KiCad Footprint / Notes | Side |
| :--- | :--- | :--- | :--- | :--- |
| **PCB** | `1` | Interposer Bare PCB | Fabricated from [`gerbers/station-g3-esp32s3eth-adapter-job.zip`](gerbers/station-g3-esp32s3eth-adapter-job.zip) | — |
| **`D1`** | `1` | SMA (`DO-214AC`) Schottky Diode (e.g., `SS14`, `SS24`, `SS34`, or `B5819W` in SMA, ≥ 1 A / ≥ 20 V) | `Diode_SMD:D_SMA_Handsoldering` — 5V reverse-current / OR-ing diode from Station G3 `5V_VSYS` to Waveshare `5V_ESP_IN` | **Top (`F.Cu`)** |
| **`J1`** | `1` | `2x20` (40-pin) 2.54 mm vertical male pin header | `PinHeader_2x20_P2.54mm_Vertical` — plugs down into Station G3 baseboard `J1` | **Bottom (`B.Cu`)** |
| **`J2`, `J3`** | `2` | `1x20` (20-pin) 2.54 mm vertical female pin sockets | `PinSocket_1x20_P2.54mm_Vertical` — Waveshare ESP32-S3-ETH plugs down into these | **Top (`F.Cu`)** |

<img width="500" alt="PXL_20261121_202200135" src="https://github.com/user-attachments/assets/b5211bc5-0026-45e1-8fdd-b4d020ea0a44" />

### Recommended Tools

* Temperature-controlled soldering iron (fine chisel or bevel tip works well)
* Rosin-core or no-clean solder (0.5 mm–0.8 mm) + liquid/gel flux
* Fine-tip tweezers (for placing `D1`)
* Flush wire cutters (optional, to trim excess header tails)
* Isopropyl alcohol (IPA ≥ 90%) and lint-free swab/brush for flux cleanup
* Digital multimeter (for diode polarity and short-circuit checks before powering on)

---

## Assembly Order Summary

1. **`D1` (SMA Schottky Diode)** on the **Top (`F.Cu`)** side (located between `J3` and `J2`) — unobstructed flat board access and clear visibility of the cathode marking.
2. **`J1` (`2x20` Male Header)** along the **outer edge of the board next to `J3`**, inserted from the **Bottom (`B.Cu`)** side and soldered on the **Top (`F.Cu`)** side — installing `J1` before `J2`/`J3` keeps the top of the PCB flat and prevents the tall `1x20` socket housing of `J3` (~5.7 mm away) from crowding your iron or getting melted while soldering `J1`'s 40 pins.
3. **`J2` and `J3` (`1x20` Female Headers)** inserted from the **Top (`F.Cu`)** side and soldered on the **Bottom (`B.Cu`)** side.

---

## Step-by-Step Instructions

### Step 1: Solder Schottky Diode `D1` (Top / `F.Cu` Side)
<img width="300" alt="PXL_20261121_202619131" src="https://github.com/user-attachments/assets/7c157adb-4ae3-40f0-88fa-bb742ca46a83" />

1. Locate **`D1`** on the **Top (`F.Cu`)** side of the PCB (same side as the `<- Ethernet` arrow and board title silkscreen).
2. **Verify polarity before soldering:**
   * The PCB silkscreen draws a **closed U-shaped bracket / bar around Pad 1** (the **cathode** pad, connected to `/5V_ESP_IN`) and leaves **Pad 2** (the **anode** pad, connected to `/5V_VSYS`) open.
   * Align the **cathode stripe/band** on the diode package with that **closed silkscreen bar (`Pad 1`)**.
   * *Tip:* If the band on your diode is hard to read, test it with a multimeter in **diode mode** first — the multimeter displays a forward voltage drop (`~0.15 V–0.35 V`) when the **red (+)** probe is on the anode and the **black (−)** probe is on the cathode band.
3. Apply a tiny dot of solder to one pad of `D1`.
4. Hold `D1` flat against the PCB with tweezers, reheat the tinned pad so the diode settles flush and centered across both pads, and remove the iron.
5. Apply a touch of flux and solder the opposite pad with a clean, shiny fillet, then briefly touch up the first pad if needed.

---

### Step 2: Solder the `2x20` Header `J1` (Bottom / `B.Cu` Side)

> **Why second?** `J1` sits along the **outer edge of the board** right beside `J3` (`~5.7 mm` center-to-center spacing), and its 40 pins are soldered from the **Top (`F.Cu`)** side. Installing `J1` before `J2` and `J3` keeps the board flat and avoids crowding or melting `J3`'s tall female socket housing with your soldering iron.
<img width="500" alt="PXL_20261121_202736195" src="https://github.com/user-attachments/assets/eca895c8-247e-406f-a42f-49115ad60945" />

1. Insert **`J1`** (`2x20` vertical male pin header) from the **Bottom (`B.Cu`)** side so the plastic spacer sits flush against the underside of the PCB and the pins protrude up through to the **Top (`F.Cu`)** side.
   * *Double-check:* The `<- Ethernet` and title silkscreen should be facing **up/away from `J1`**.
2. Set the board gently upside-down or prop the edges slightly off your mat so the pins stay pushed flush through the board without resting directly on `D1`.
3. On the **Top (`F.Cu`)** side, solder **one corner pin** only.
4. Pick up the board and confirm `J1` sits completely **flat** against the bottom of the PCB and **square (`90°`)**. If it is tilted, reheat that single pin while pressing the header gently into alignment.
 <img width="500" alt="PXL_20261121_202746656" src="https://github.com/user-attachments/assets/51cce2aa-d43e-4da9-8069-7f3a40238537" />
  
6. Solder the diagonally opposite corner pin, re-check flatness, and then solder all remaining 38 pins on the **Top (`F.Cu`)** side.

---

### Step 3: Solder the Two `1x20` Female Headers `J2` & `J3` (Top / `F.Cu` Side)
<img width="500"  alt="PXL_20261121_204345379" src="https://github.com/user-attachments/assets/648a514d-1ae7-4c91-b2fc-43f3912465b3" />

1. Insert both **`J2`** and **`J3`** (`1x20` vertical female sockets) from the **Top (`F.Cu`)** side so their plastic housings sit on the same side as `D1` and the silkscreen text, with solder tails extending down through to the **Bottom (`B.Cu`)** side.
2. **Alignment Jig (Recommended):**
   * Lightly plug the **Waveshare ESP32-S3-ETH** module (or two spare straight `1x20` male header strips - such as those that come with Heltec boards) into `J2` and `J3` before soldering. This guarantees both sockets stay parallel and spaced identically to the Waveshare pins.
   * Confirm the Waveshare board's RJ45 Ethernet jack points in the direction of the **`<- Ethernet`** arrow on the top silkscreen (`F.SilkS`).
3. Keep the sockets pressed flush against the top of the PCB, turn the assembly over, and tack **one end pin on `J2`** and **one end pin on `J3`** from the **Bottom (`B.Cu`)** side.
4. Check from both ends that `J2` and `J3` sit completely flush against the PCB and parallel.
5. Tack the opposite end pins of `J2` and `J3`.
6. **Unplug the Waveshare module** before soldering the rest of the pins (prevents heat transfer into the module and makes handling easier), then solder all remaining pins along `J2` (one `1x20` row) and `J3` (second `1x20` row) from the **Bottom (`B.Cu`)** side.

---

## Pre-Power Inspection & Continuity Checks

Before installing the interposer onto the Station G3 or Waveshare module:

1. **Clean flux residue** with IPA and a soft brush, especially around `D1` and between the `J1` pins.
2. **Visual check** under good light or magnification for cold joints, missed pins, or solder bridges.
3. **Multimeter checks (board unpopulated and unpowered):**
   * **No dead shorts:** Check resistance between **`GND`** (`J1` Pin 6), **`3V3_LOGIC`** (`J1` Pin 1), and **`5V_VSYS`** (`J1` Pin 2) — none should beep continuous short.
   * **`D1` polarity check:** In diode mode, place the **red (+)** probe on `J1` Pin 2 (`5V_VSYS`) and the **black (−)** probe on `J3` Pin 39 (`5V_ESP_IN`). You should measure a Schottky forward drop (`~0.15 V–0.35 V`). Reversing the probes should read open / `OL`.
<img width="500" alt="PXL_20261113_202111552" src="https://github.com/user-attachments/assets/fbd5aa59-2cc0-495d-902c-fe3c5c48d12f" />

---

## Final Module Mating & Installation
<img width="500" alt="PXL_20261113_202143425" src="https://github.com/user-attachments/assets/03d9d32b-5abe-43bc-a245-33be04a4bc13" />

1. Press the **Waveshare ESP32-S3-ETH** firmly into `J2` and `J3` on the top of the interposer, verifying the RJ45 Ethernet port faces the **`<- Ethernet`** silkscreen arrow.
<img width="300" alt="PXL_20261113_203229811" src="https://github.com/user-attachments/assets/1223fed8-4858-459a-912f-8a1b3c374122" />

2. Align **`J1`** on the bottom of the interposer with the **`J1` (`2x20`)** header on the **Station G3 Baseboard**, verifying all 40 pins line up with no shifted rows or columns, and press down evenly until seated. Install the 3 screws to secure.
3. Refer to the main [`README.md`](../README.md#flashing-instructions) to flash the firmware.
