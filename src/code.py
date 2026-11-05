import os
import time
import gc
import math
import array
import sys
import supervisor
import board
import pwmio
import audiopwmio
import synthio
import usb_midi
import adafruit_midi
import config

print(f"🚀 {config.DEVICE_NAME} Initializing...")

# 1. Hardware Output Setup
audio_out = audiopwmio.PWMAudioOut(config.AUDIO_PWM_PIN)
synth = synthio.Synthesizer(sample_rate=config.SAMPLE_RATE)
audio_out.play(synth)

# 2. 600 kHz AM Carrier Setup on GP14
carrier = pwmio.PWMOut(
    config.AM_CARRIER_PIN, 
    frequency=config.AM_CARRIER_FREQ,
    duty_cycle=32768,
    variable_frequency=False
)

# 3. Expanded Instrument Names Mapping (0 - 15)
INSTRUMENT_NAMES = [
    "E-Piano",          # 0
    "Brass / Lead",     # 1
    "Acoustic Vibes",   # 2
    "Chiptune Square",  # 3
    "Plucked Guitar",   # 4
    "Accordion Reed",   # 5
    "Warm Organ",       # 6
    "Metallic Bell",    # 7
    "Deep Synth Bass",  # 8
    "Warm Soft Pad",    # 9
    "Funky Clav",       # 10
    "Soft Flute",       # 11
    "Distorted Lead",   # 12
    "Slap Bass",        # 13
    "80s Synth Brass",  # 14
    "Sci-Fi Chime"      # 15
]

# Gain normalization multipliers for all 16 patches
PATCH_GAINS = [
    0.85, 0.65, 0.90, 0.60, 0.95, 0.70, 0.65, 0.75, 
    1.00, 0.80, 0.75, 0.90, 0.55, 0.90, 0.60, 0.70
]

# 4. Generate 16 Distinct Synthesized Waveforms
def build_waveform_bank(length=32):
    waves = []
    
    # 0: E-Piano
    waves.append(array.array("h", [int(32767 * math.sin(2 * math.pi * i / length)) for i in range(length)]))
    
    # 1: Bright Lead
    waves.append(array.array("h", [int(-32767 + (65534 * i / (length - 1))) for i in range(length)]))
    
    # 2: Acoustic Vibes
    tri = []
    half = length // 2
    for i in range(length):
        if i < half:
            tri.append(-32767 + int(65534 * (i / half)))
        else:
            tri.append(32767 - int(65534 * ((i - half) / half)))
    waves.append(array.array("h", tri))
    
    # 3: Chiptune Square
    waves.append(array.array("h", [32767 if i < length // 2 else -32767 for i in range(length)]))
    
    # 4: Plucked Guitar
    waves.append(array.array("h", [32767 if i < length // 4 else -32767 for i in range(length)]))
    
    # 5: Accordion Reed
    waves.append(array.array("h", [32767 if i < length // 8 else -32767 for i in range(length)]))
    
    # 6: Warm Organ
    org = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.5 * math.sin(4 * math.pi * i / length) + 0.3 * math.sin(6 * math.pi * i / length)) / 1.8
        org.append(int(32767 * v))
    waves.append(array.array("h", org))
    
    # 7: Metallic Bell
    bell = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.7 * math.sin(7 * math.pi * i / length)) / 1.7
        bell.append(int(32767 * v))
    waves.append(array.array("h", bell))
    
    # 8: Deep Synth Bass
    bass = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.6 * math.sin(4 * math.pi * i / length)) / 1.6
        bass.append(int(32767 * v))
    waves.append(array.array("h", bass))
    
    # 9: Warm Soft Pad
    pad = []
    for i in range(length):
        v = math.sin(2 * math.pi * i / length) * 0.85
        pad.append(int(32767 * v))
    waves.append(array.array("h", pad))

    # 10: Funky Clav
    waves.append(array.array("h", [32767 if i < length // 16 else -32767 for i in range(length)]))

    # 11: Soft Flute
    flute = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.2 * math.sin(4 * math.pi * i / length)) / 1.2
        flute.append(int(32767 * v))
    waves.append(array.array("h", flute))

    # 12: Distorted Lead
    dist = []
    for i in range(length):
        raw = -32767 + (65534 * i / (length - 1))
        dist.append(int(max(-26000, min(26000, raw * 2))))
    waves.append(array.array("h", dist))

    # 13: Slap Bass
    slap = []
    for i in range(length):
        v = math.sin(2 * math.pi * i / length) + (0.5 if i < 3 else 0.0)
        slap.append(int(32767 * max(-1.0, min(1.0, v))))
    waves.append(array.array("h", slap))

    # 14: 80s Synth Brass
    sbrass = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.8 * math.sin(3 * math.pi * i / length) + 0.4 * math.sin(5 * math.pi * i / length)) / 2.2
        sbrass.append(int(32767 * v))
    waves.append(array.array("h", sbrass))

    # 15: Sci-Fi Chime
    scifi = []
    for i in range(length):
        v = (math.sin(2 * math.pi * i / length) + 0.9 * math.sin(5.3 * math.pi * i / length)) / 1.9
        scifi.append(int(32767 * v))
    waves.append(array.array("h", scifi))
    
    return waves

WAVE_BANK = build_waveform_bank()

# 5. ADSR Envelopes
ENVELOPE_BANK = [
    synthio.Envelope(attack_time=0.01, decay_time=0.25, sustain_level=0.5, release_time=0.20),
    synthio.Envelope(attack_time=0.03, decay_time=0.15, sustain_level=0.8, release_time=0.15),
    synthio.Envelope(attack_time=0.02, decay_time=0.20, sustain_level=0.6, release_time=0.25),
    synthio.Envelope(attack_time=0.00, decay_time=0.10, sustain_level=0.7, release_time=0.05),
    synthio.Envelope(attack_time=0.00, decay_time=0.18, sustain_level=0.1, release_time=0.10),
    synthio.Envelope(attack_time=0.02, decay_time=0.10, sustain_level=0.7, release_time=0.10),
    synthio.Envelope(attack_time=0.01, decay_time=0.05, sustain_level=0.9, release_time=0.10),
    synthio.Envelope(attack_time=0.00, decay_time=0.40, sustain_level=0.2, release_time=0.30),
    synthio.Envelope(attack_time=0.01, decay_time=0.15, sustain_level=0.7, release_time=0.10),
    synthio.Envelope(attack_time=0.15, decay_time=0.30, sustain_level=0.8, release_time=0.40),
    synthio.Envelope(attack_time=0.00, decay_time=0.12, sustain_level=0.3, release_time=0.08),
    synthio.Envelope(attack_time=0.08, decay_time=0.20, sustain_level=0.8, release_time=0.20),
    synthio.Envelope(attack_time=0.01, decay_time=0.10, sustain_level=0.9, release_time=0.10),
    synthio.Envelope(attack_time=0.00, decay_time=0.15, sustain_level=0.4, release_time=0.08),
    synthio.Envelope(attack_time=0.04, decay_time=0.20, sustain_level=0.7, release_time=0.20),
    synthio.Envelope(attack_time=0.00, decay_time=0.50, sustain_level=0.1, release_time=0.40)
]

def get_ai_patch(channel, note_val, song_seed=0):
    if channel == 9:
        return 13 if (note_val % 2 == 0) else 8
    if note_val < 42:
        return 8
    if note_val < 50:
        return 13
    if note_val > 84:
        return 15 if (note_val % 2 == 0) else 7
    if note_val > 72:
        return 11 if (channel % 2 == 0) else 12
        
    return (channel + song_seed) % 16

channel_pitch_bends = {ch: 1.0 for ch in range(16)}

# 6. USB MIDI Setup
midi_in = None
if usb_midi.ports and len(usb_midi.ports) > 0:
    midi_in = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=0)

active_file_notes = {}
active_live_notes = {}
MAX_POLYPHONY = config.MAX_POLYPHONY

# 7. Folder Scanner
playlist = []

try:
    all_files = sorted(os.listdir(config.MIDI_DIR))
    for filename in all_files:
        if filename.lower().endswith((".mid", ".midi")):
            playlist.append(filename)
            if len(playlist) >= 20:
                break
except OSError:
    print(f"❌ ERROR: Could not find '{config.MIDI_DIR}' directory!")

if not playlist:
    print(f"⚠️ WARNING: No .mid files found inside {config.MIDI_DIR} folder!")
else:
    print(f"📁 Loaded playlist cache: Found {len(playlist)} track(s).")


def check_serial_skip():
    """Non-blocking keyboard reader: returns True if 'y' is pressed, False if 'n'."""
    if supervisor.runtime.serial_bytes_available:
        char = sys.stdin.read(1).lower()
        if char == 'y':
            print("\n⏭️ ['y' pressed] Skipping to next track...")
            return True
        elif char == 'n':
            print("\n▶️ ['n' pressed] Continuing track...")
    return False


def process_live_midi():
    """Service live incoming USB MIDI input."""
    if midi_in is None:
        return
    try:
        msg = midi_in.receive()
        if msg is not None:
            msg_type = type(msg).__name__
            channel = getattr(msg, "channel", 0)
            
            if msg_type == "NoteOn" and getattr(msg, "velocity", 0) > 0:
                note_val = msg.note
                velocity = msg.velocity
                note_key = (channel, note_val)
                
                if note_key in active_live_notes:
                    synth.release(active_live_notes[note_key])
                
                patch_id = get_ai_patch(channel, note_val)
                bend_mult = channel_pitch_bends.get(channel, 1.0)
                freq = synthio.midi_to_hz(note_val) * bend_mult
                
                amp = ((velocity / 127.0) ** 1.2) * PATCH_GAINS[patch_id]
                
                note_obj = synthio.Note(
                    frequency=freq, 
                    waveform=WAVE_BANK[patch_id], 
                    envelope=ENVELOPE_BANK[patch_id],
                    amplitude=min(1.0, max(0.05, amp))
                )
                active_live_notes[note_key] = note_obj
                synth.press(note_obj)
                
            elif msg_type == "NoteOff" or (msg_type == "NoteOn" and getattr(msg, "velocity", 0) == 0):
                note_val = msg.note
                note_key = (channel, note_val)
                if note_key in active_live_notes:
                    synth.release(active_live_notes[note_key])
                    del active_live_notes[note_key]
                    
            elif msg_type == "PitchBend":
                bend_val = msg.pitch_bend
                semitones = ((bend_val - 8192) / 8192.0) * 2.0
                bend_mult = 2.0 ** (semitones / 12.0)
                channel_pitch_bends[channel] = bend_mult
                
                for (ch, n_val), note_obj in active_live_notes.items():
                    if ch == channel:
                        note_obj.frequency = synthio.midi_to_hz(n_val) * bend_mult

    except Exception:
        pass


def non_blocking_wait_until(target_time):
    """Wait until target timestamp while servicing MIDI input and serial keyboard skips."""
    while time.monotonic() < target_time:
        if check_serial_skip():
            return True
        process_live_midi()
        time.sleep(0.001)
    return False


class TrackStreamer:
    def __init__(self, file_handle, start_pos, track_len):
        self.f = file_handle
        self.pos = start_pos
        self.end_pos = start_pos + track_len
        self.abs_tick = 0
        self.running_status = None
        self.done = False

    def read_varlen(self):
        val = 0
        while self.pos < self.end_pos:
            self.f.seek(self.pos)
            b = self.f.read(1)
            if not b:
                self.done = True
                return 0
            self.pos += 1
            byte = b[0]
            val = (val << 7) | (byte & 0x7F)
            if not (byte & 0x80):
                break
        return val

    def peek_next_delta(self):
        if self.pos >= self.end_pos or self.done:
            self.done = True
            return False
        delta = self.read_varlen()
        self.abs_tick += delta
        return True

    def read_event(self):
        if self.done or self.pos >= self.end_pos:
            self.done = True
            return None

        self.f.seek(self.pos)
        b = self.f.read(1)
        if not b:
            self.done = True
            return None

        status_byte = b[0]
        self.pos += 1

        if status_byte >= 0x80:
            status = status_byte
            if status < 0xF0:
                self.running_status = status
            else:
                self.running_status = None
        else:
            if self.running_status is None:
                self.peek_next_delta()
                return None
            status = self.running_status
            self.pos -= 1

        cmd = status & 0xF0
        channel = status & 0x0F

        event = None
        if cmd in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
            self.f.seek(self.pos)
            data_bytes = self.f.read(2)
            self.pos += len(data_bytes)
            if len(data_bytes) == 2:
                event = (cmd, channel, data_bytes[0], data_bytes[1])
        elif cmd in (0xC0, 0xD0):
            self.pos += 1
        elif status == 0xFF:
            self.f.seek(self.pos)
            meta_b = self.f.read(1)
            self.pos += len(meta_b)
            if meta_b:
                meta_type = meta_b[0]
                meta_len = self.read_varlen()
                self.f.seek(self.pos)
                meta_data = self.f.read(meta_len)
                self.pos += len(meta_data)
                if meta_type == 0x51 and len(meta_data) >= 3:
                    us_pq = (meta_data[0] << 16) | (meta_data[1] << 8) | meta_data[2]
                    event = (0xFF, 0x51, us_pq)
        elif status in (0xF0, 0xF7):
            sys_len = self.read_varlen()
            self.pos += sys_len

        self.peek_next_delta()
        return event


def get_track_locations(f):
    f.seek(0)
    hdr = f.read(14)
    if len(hdr) < 14 or hdr[:4] != b'MThd':
        raise ValueError("Invalid MIDI header")

    num_tracks = (hdr[10] << 8) | hdr[11]
    ticks_per_quarter = (hdr[12] << 8) | hdr[13]
    if ticks_per_quarter & 0x8000:
        ticks_per_quarter = 480

    tracks = []
    pos = 14
    for _ in range(num_tracks):
        f.seek(pos)
        chunk_hdr = f.read(8)
        if not chunk_hdr or len(chunk_hdr) < 8:
            break
        chunk_type = chunk_hdr[:4]
        chunk_len = int.from_bytes(chunk_hdr[4:8], 'big')
        if chunk_type == b'MTrk':
            tracks.append((pos + 8, chunk_len))
        pos += 8 + chunk_len

    return tracks, ticks_per_quarter


def scan_band_lineup(f, track_info, song_index):
    streamers = [TrackStreamer(f, start, length) for start, length in track_info]
    for st in streamers:
        st.peek_next_delta()

    used_patches = {}
    first_note_tick = 0
    found_first_note = False

    while True:
        active = [s for s in streamers if not s.done]
        if not active:
            break
        min_st = min(active, key=lambda s: s.abs_tick)
        evt = min_st.read_event()
        
        if evt and evt[0] == 0x90 and evt[3] > 0:
            if not found_first_note:
                first_note_tick = min_st.abs_tick
                found_first_note = True
            
            channel, note_val = evt[1], evt[2]
            patch_id = get_ai_patch(channel, note_val, song_seed=song_index)
            used_patches[patch_id] = used_patches.get(patch_id, 0) + 1

    print("┌──────────────────────────────────────────────┐")
    print("│ 🎷 AI BAND INSTRUMENT LINEUP                 │")
    print("├──────────────────────────────────────────────┤")
    for patch_id, count in sorted(used_patches.items(), key=lambda x: x[1], reverse=True):
        inst_name = INSTRUMENT_NAMES[patch_id]
        print(f"│  • {inst_name:<18} ({count:>4} notes)    │")
    print("└──────────────────────────────────────────────┘")

    return first_note_tick


def play_midi_file(filepath, song_index):
    global active_file_notes, channel_pitch_bends
    gc.collect()

    channel_pitch_bends = {ch: 1.0 for ch in range(16)}

    try:
        with open(filepath, "rb") as f:
            track_info, ticks_per_quarter = get_track_locations(f)
            first_note_tick = scan_band_lineup(f, track_info, song_index)

            streamers = [TrackStreamer(f, start, length) for start, length in track_info]
            for st in streamers:
                st.peek_next_delta()

            us_per_quarter = 500000
            current_tick = first_note_tick
            accumulated_time = 0.0
            start_monotonic = time.monotonic()

            while True:
                active_streamers = [st for st in streamers if not st.done]
                if not active_streamers:
                    break

                min_st = min(active_streamers, key=lambda s: s.abs_tick)
                abs_tick = min_st.abs_tick
                evt = min_st.read_event()

                if evt is None:
                    continue

                cmd = evt[0]

                if abs_tick < first_note_tick:
                    if cmd == 0xFF and evt[1] == 0x51:
                        us_per_quarter = evt[2]
                    continue

                delta_ticks = abs_tick - current_tick
                if delta_ticks > 0:
                    delta_sec = (delta_ticks * us_per_quarter) / (ticks_per_quarter * 1000000.0)
                    accumulated_time += delta_sec
                    current_tick = abs_tick

                    target_time = start_monotonic + accumulated_time
                    should_skip = non_blocking_wait_until(target_time)
                    if should_skip:
                        break

                if cmd == 0x90:  # Note On
                    channel, note_val, velocity = evt[1], evt[2], evt[3]
                    note_key = (channel, note_val)
                    if velocity > 0:
                        if note_key in active_file_notes:
                            synth.release(active_file_notes[note_key])

                        if len(active_file_notes) >= MAX_POLYPHONY:
                            oldest_key = next(iter(active_file_notes))
                            synth.release(active_file_notes[oldest_key])
                            del active_file_notes[oldest_key]

                        patch_id = get_ai_patch(channel, note_val, song_seed=song_index)
                        bend_mult = channel_pitch_bends.get(channel, 1.0)
                        freq = synthio.midi_to_hz(note_val) * bend_mult
                        
                        amp = ((velocity / 127.0) ** 1.2) * PATCH_GAINS[patch_id]
                        
                        note_obj = synthio.Note(
                            frequency=freq, 
                            waveform=WAVE_BANK[patch_id],
                            envelope=ENVELOPE_BANK[patch_id],
                            amplitude=min(1.0, max(0.05, amp))
                        )
                        active_file_notes[note_key] = note_obj
                        synth.press(note_obj)
                    else:
                        if note_key in active_file_notes:
                            synth.release(active_file_notes[note_key])
                            del active_file_notes[note_key]

                elif cmd == 0x80:  # Note Off
                    channel, note_val = evt[1], evt[2]
                    note_key = (channel, note_val)
                    if note_key in active_file_notes:
                        synth.release(active_file_notes[note_key])
                        del active_file_notes[note_key]

                elif cmd == 0xE0:  # Pitch Bend
                    channel = evt[1]
                    d1, d2 = evt[2], evt[3]
                    bend_val = (d2 << 7) | d1
                    semitones = ((bend_val - 8192) / 8192.0) * 2.0
                    bend_mult = 2.0 ** (semitones / 12.0)
                    channel_pitch_bends[channel] = bend_mult
                    
                    for (ch, n_val), note_obj in active_file_notes.items():
                        if ch == channel:
                            note_obj.frequency = synthio.midi_to_hz(n_val) * bend_mult

                elif cmd == 0xFF and evt[1] == 0x51:  # Tempo Change
                    us_per_quarter = evt[2]

    except Exception as e:
        print(f"💥 Skipping file error: {type(e).__name__} - {e}")

    # Release all active file notes on track end or skip
    for note_obj in active_file_notes.values():
        synth.release(note_obj)
    active_file_notes.clear()


# Main Playback Loop
current_track_index = 0

while True:
    if not playlist:
        print(f"💤 Standing by... Put .mid tracks into '{config.MIDI_DIR}'.")
        non_blocking_wait_until(time.monotonic() + 5.0)
        try:
            all_files = sorted(os.listdir(config.MIDI_DIR))
            playlist = [f for f in all_files if f.lower().endswith((".mid", ".midi"))][:20]
        except OSError:
            pass
        continue

    song_filename = playlist[current_track_index]
    full_path = f"{config.MIDI_DIR}/{song_filename}"

    print(f"\n📻 Broadcasting Track {current_track_index + 1}/{len(playlist)}: '{song_filename}'")
    print("⌨️ Press 'y' anytime to skip track ('n' to acknowledge/continue)...")

    play_midi_file(full_path, song_index=current_track_index)
    print(f"✨ Track {current_track_index + 1} finished.")

    current_track_index = (current_track_index + 1) % len(playlist)
    
    # 2.5s gap between tracks (also skippable instantly with 'y')
    skipped = non_blocking_wait_until(time.monotonic() + 2.5)
