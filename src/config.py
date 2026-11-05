# SFB Dynamics: AM Beacon & Synth System Parameters
import board

# System Information
DEVICE_NAME = "SFB Dynamics 20-Song MIDI Station"
BEACON_ID = "SFB-MIDI-BEACON-01"

# Hardware Pin Mapping
AUDIO_PWM_PIN = board.GP16      # Audio output (connect to RC filter / headphone jack)
AM_CARRIER_PIN = board.GP14     # 600 kHz AM radio broadcast carrier output

# Frequency & Audio Configuration
AM_CARRIER_FREQ = 600000        # 600 kHz AM Band (Medium-Wave Broadcast)
SAMPLE_RATE = 22050             # 22.05 kHz synthesis sample rate
MAX_POLYPHONY = 12              # Maximum concurrent synth voices

# Storage & File System Paths
MIDI_DIR = "/midi"              # Folder on Pico drive containing .mid tracks
