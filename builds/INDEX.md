# Meshtastic Custom Firmware Builds Index

> **Last Pipeline Sync:** `2026-11-06 06:07:43 UTC`  
> **Active Release Folders:** `alpha-v2.8.2.d5f1619`, `beta-v2.7.26.54e0d8d`

This directory contains automated, overlay-patched firmware binaries compiled by the CI/CD pipeline.
Outdated release directories not matching active retention rules are automatically pruned.

---

## Available Firmware Builds

| Channel | Tag | Type | Variant | Target PIO Env | Applied PRs | Local Patches | Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ALPHA** | [`v2.8.2.d5f1619`](https://github.com/meshtastic/firmware/releases/tag/v2.8.2.d5f1619) | `vanilla` | **station-g3-waveshare-eth** | `station-g3-waveshare-eth` | _None_ | `station-g3-eth-ota.patch` | [`station-g3-waveshare-eth/`](alpha-v2.8.2.d5f1619/vanilla/station-g3-waveshare-eth/)<br>[`firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin`](alpha-v2.8.2.d5f1619/vanilla/station-g3-waveshare-eth/firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin)<br>[`firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin`](alpha-v2.8.2.d5f1619/vanilla/station-g3-waveshare-eth/firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin)<br>[`littlefs-station-g3-waveshare-eth-2.8.2.d5f1619.bin`](alpha-v2.8.2.d5f1619/vanilla/station-g3-waveshare-eth/littlefs-station-g3-waveshare-eth-2.8.2.d5f1619.bin)<br>[`mt-esp32s3-ota.bin`](alpha-v2.8.2.d5f1619/vanilla/station-g3-waveshare-eth/mt-esp32s3-ota.bin) |

---

### Detailed Build Manifest Information

Each variant directory includes a `build-manifest.json` file documenting the exact upstream git commit SHA, build timestamp, and applied modifications for provenance and reproducibility.
