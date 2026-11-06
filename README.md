# SFBDynamics
MicroPython firmware and hardware schematics for Raspberry Pi Pico radio and beacon nodes.
# SFB Dynamics: AM Synth & MIDI Beacon Station

Universal 20-Song MIDI Synthesizer and 600 kHz AM Carrier Broadcast Engine powered by the Raspberry Pi Pico.

## Features
* **16-Instrument AI Sound Engine:** Dynamic patch allocation using `synthio`.
* **AM Carrier Generation:** Hardware PWM output on `GP14` (600 kHz medium-wave AM band).
* **Polyphonic Audio Output:** Dual PWM audio synthesis on `GP16`.
* **Low-Memory MIDI Streaming:** Direct SD/Flash binary `.mid` streaming with 12-voice polyphony management.

## Firmware & Setup
1. Flash your Raspberry Pi Pico with **CircuitPython 9.x** (or 8.x).
2. Copy the contents of `/src/` to your Pico drive root.
3. Ensure `/lib/adafruit_midi` is present on the Pico drive.
4. Place up to 20 `.mid` files inside a `/midi` folder on the Pico drive.

5. ## Licensing & Copyright

© 2026 **SFB Dynamics**. All rights reserved.

This project is released under the **PolyForm Noncommercial License 1.0.0**. 

* **Permitted:** Personal testing, educational use, non-commercial hardware builds, and code modifications for private use.
* **Prohibited:** Commercial sales, selling pre-built boards/kits, paid distribution, or incorporating any code/designs into commercial products without explicit written permission from SFB Dynamics.
