# SFB Dynamics: Hardware Wiring & Pinout Guide

## Raspberry Pi Pico Pin Mapping

| Pico Pin | Function | External Component | Description |
| :--- | :--- | :--- | :--- |
| **GP14 (Pin 19)** | 600 kHz AM Carrier Output | RF Antenna / Modulator input | 50% Duty cycle square wave at 600 kHz |
| **GP16 (Pin 21)** | PWM Audio Synth Output | Low-pass RC Filter / 3.5mm Jack | 22.05 kHz 16-bit `synthio` audio stream |
| **GND (Pin 23)** | System Ground | Ground reference | Common ground connection for audio/RF |
| **VBUS / 3V3** | Power Input | USB Power or LiPo Battery | 5V via micro-USB / 3.3V power pin |

## Basic RC Audio Filter Circuit

To convert the `GP16` digital PWM audio into smooth analog sound for headphones or speakers:
