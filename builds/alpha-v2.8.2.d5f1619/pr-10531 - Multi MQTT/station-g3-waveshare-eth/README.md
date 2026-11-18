# PR Build: pr-10531 - Multi MQTT

> **Target Release:** `alpha-v2.8.2.d5f1619`  
> **Generated:** `2026-11-18 20:38:16 UTC`  
> **Profile Summary:** Allow MQTT uplinks to uplink multiple copies of packets  

---

## Upstream Pull Request Details

### [PR #10531: Add a way to have MQTT uplinks uplink multiple copies of packets](https://github.com/meshtastic/firmware/pull/10531)
* **Author:** [@ianmcorvidae](https://github.com/ianmcorvidae)
* **PR Link:** https://github.com/meshtastic/firmware/pull/10531

#### Description

... when they're heard multiple times (hidden behind compile flag + userPrefs)

This is entirely for MQTT-based analytics. Uplinking packets multiple times means analytics tools and users can see SNRs for rebroadcasts after the first heard by each uplink, and it's especially useful for traceroutes, where entire paths that might otherwise not appear can come by way of later-heard copies of the packet.

My experience level with C++ is not amazing so I'm suspecting there are things here that aren't needed, despite my best efforts to rein in the generated code. The primary parts of this PR are just moving MQTT uplink logic into a dedicated `Router::publishReceivedToMqtt` and then calling it from a variety of places to catch packets that otherwise wouldn't make it to the regular uplink location.

Some specific question areas are the necessity of lines 870-874 in Router.cpp, serving as a dummy implementation I guess, and whether the gate on MQTT being enabled at all should be moved to live outside the newly created function. I'll try to test it on a few more devices, but it's also not a huge change and it works on at least one esp32 and nrf52, so I'm not too worried it'll turn up issues.

## 🤝 Attestations

- [x] I have tested that my proposed changes behave as described.
- [ ] I have tested that my proposed changes do not cause any obvious regressions on the following devices:
  - [ ] Heltec (Lora32) V3
  - [ ] LilyGo T-Deck
  - [ ] LilyGo T-Beam
  - [ ] RAK WisBlock 4631
  - [x] Seeed Studio T-1000E tracker card
  - [x] Other (please specify below) (LilyGo t3s3 v1)

---

## Included Board Variants

| Variant | Files Available |
| :--- | :--- |
| [`station-g3-waveshare-eth/`](station-g3-waveshare-eth/) | `device-install.bat`, `device-install.sh`, `device-update.bat`, `device-update.sh`, `firmware-station-g3-waveshare-eth-2.8.2.d5f1619.bin`, `firmware-station-g3-waveshare-eth-2.8.2.d5f1619.factory.bin`, `firmware-station-g3-waveshare-eth-2.8.2.d5f1619.full.bin`, `littlefs-station-g3-waveshare-eth-2.8.2.d5f1619.bin`, `mt-esp32s3-ota.bin`, `sha256sums.txt` |
