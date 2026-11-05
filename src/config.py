# SFB Dynamics: Pico Beacon Configuration Settings

# Device Identification
BEACON_ID = "SFB-NODE-01"
DEVICE_NAME = "Small Form Beacon Pico"

# Radio Transmission Parameters
FREQUENCY_MHZ = 433.92        # Standard unlicensed ISM band
TX_INTERVAL_SECONDS = 5       # Delay between beacon pulses
TX_POWER_LEVEL = "LOW"        # Keeps power within low-power rules

# Pin Definitions (Raspberry Pi Pico RP2040)
STATUS_LED_PIN = 25           # Onboard LED pin
RF_TX_PIN = 15                # Digital transmit trigger pin
