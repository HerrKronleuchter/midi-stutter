import struct
from pathlib import Path
from config import CONFIG


def var_len(value):
    """Encode variable-length MIDI value"""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


def note_on(tick, channel, note, velocity):
    return var_len(tick) + bytes([0x90 | channel, note, velocity])


def note_off(tick, channel, note):
    return var_len(tick) + bytes([0x80 | channel, note, 0])


def make_midi(notes_data, tempo=120, ticks_per_beat=480):
    """
    notes_data: list of (pos_beats, len_beats, pitch, velocity)
    """
    # Convert to tick events
    events = []
    for pos, length, pitch, vel in notes_data:
        on_tick = round(pos * ticks_per_beat)
        off_tick = round((pos + length) * ticks_per_beat)
        events.append((on_tick, "on", pitch, vel))
        events.append((off_tick, "off", pitch, 0))

    events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

    # Build track bytes with delta times
    track_data = b""
    prev_tick = 0
    for tick, kind, pitch, vel in events:
        delta = tick - prev_tick
        prev_tick = tick
        if kind == "on":
            track_data += var_len(delta) + bytes([0x90, pitch, vel])
        else:
            track_data += var_len(delta) + bytes([0x80, pitch, 0])

    # End of track
    track_data += b"\x00\xff\x2f\x00"

    # Tempo meta event (microseconds per beat)
    us_per_beat = round(60_000_000 / tempo)
    tempo_event = b"\x00\xff\x51\x03" + struct.pack(">I", us_per_beat)[1:]

    # Time signature 4/4
    timesig_event = b"\x00\xff\x58\x04\x04\x02\x18\x08"

    full_track = tempo_event + timesig_event + track_data

    # MIDI header chunk
    header = b"MThd" + struct.pack(">I", 6) + struct.pack(">HHH", 0, 1, ticks_per_beat)

    # Track chunk
    track_chunk = b"MTrk" + struct.pack(">I", len(full_track)) + full_track

    return header + track_chunk


if __name__ == "__main__":

    """Generate stutter pattern MIDI file"""
    # TODO: Parameters
    start_note = 61
    start_len = 1
    factor = 0.94
    num_notes = 128
    tempo = 127
    base_velocity = 110
    vel_decay_exp = 0.15
    out_dir = CONFIG["out_dir"]

    notes_data = []
    pos = 0.0
    length = start_len

    for i in range(num_notes):
        if length < 0.02:
            break
        # Velocity decreases slightly with each note
        vel = max(
            30,
            round(base_velocity * (factor ** (i * vel_decay_exp))),
        )
        notes_data.append((pos, length * 0.92, start_note, vel))  # 0.92 = slight gap
        pos += length
        length *= factor

    midi_bytes = make_midi(notes_data, tempo=tempo)

    # Generate filename
    filename = f"stutter_{tempo}_{factor}.mid"

    file_path = out_dir / filename

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(midi_bytes)

    print(f"MIDI written: {file_path}")
    print(f"Notes: {len(notes_data)}")
    for i, (p, l, pitch, vel) in enumerate(notes_data):
        print(f"  Note {i+1}: pos={p:.4f} beats, len={l:.4f} beats, vel={vel}")
