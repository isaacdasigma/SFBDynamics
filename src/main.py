# Main entry point for Pico firmware
# SFB Dynamics: Pico Beacon Main Transmission Loop
from machine import Pin
import time
import config

# Initialize hardware pins
led = Pin(config.STATUS_LED_PIN, Pin.OUT)
tx_pin = Pin(config.RF_TX_PIN, Pin.OUT)

def send_beacon_pulse():
    """Simulates a short radio signal transmission pulse."""
    print(f"[{config.BEACON_ID}] Transmitting beacon ping on {config.FREQUENCY_MHZ} MHz...")
    
    # Indicate transmission start
    led.value(1)
    tx_pin.value(1)
    time.sleep(0.2)  # Pulse duration
    
    # End transmission
    tx_pin.value(0)
    led.value(0)

print(f"Starting {config.DEVICE_NAME}...")
print("System ready. Entering transmission loop.")

while True:
    send_beacon_pulse()
    time.sleep(config.TX_INTERVAL_SECONDS)
