import struct
import click
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


def make_midi(notes_data, tempo=120, ticks_per_beat=480):
    events = []
    for pos, length, pitch, vel in notes_data:
        on_tick = round(pos * ticks_per_beat)
        off_tick = round((pos + length) * ticks_per_beat)
        events.append((on_tick, "on", pitch, vel))
        events.append((off_tick, "off", pitch, 0))
    events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

    track_data = b""
    prev_tick = 0
    for tick, kind, pitch, vel in events:
        delta = tick - prev_tick
        prev_tick = tick
        if kind == "on":
            track_data += var_len(delta) + bytes([0x90, pitch, vel])
        else:
            track_data += var_len(delta) + bytes([0x80, pitch, 0])

    track_data += b"\x00\xff\x2f\x00"

    us_per_beat = round(60_000_000 / tempo)
    tempo_event = b"\x00\xff\x51\x03" + struct.pack(">I", us_per_beat)[1:]
    timesig_event = b"\x00\xff\x58\x04\x04\x02\x18\x08"
    full_track = tempo_event + timesig_event + track_data

    header = b"MThd" + struct.pack(">I", 6) + struct.pack(">HHH", 0, 1, ticks_per_beat)
    track_chunk = b"MTrk" + struct.pack(">I", len(full_track)) + full_track
    return header + track_chunk


@click.command()
@click.option(
    "--bpm", prompt="BPM", default=127, show_default=True, type=int, help="Tempo in BPM"
)
@click.option(
    "--note",
    prompt="Start note (MIDI)",
    default=36,
    show_default=True,
    type=int,
    help="MIDI note number 0–127, C1 is 36, C2 is 48, C4 is 60, ...",
)
@click.option(
    "--start-len",
    prompt="Start length (beats)",
    default=1.0,
    show_default=True,
    type=float,
    help="Initial note length in beats",
)
@click.option(
    "--factor",
    prompt="Decay factor",
    default=0.94,
    show_default=True,
    type=float,
    help="Length multiplier per step (0–1)",
)
@click.option(
    "--num-notes",
    prompt="Note count",
    default=128,
    show_default=True,
    type=int,
    help="Max number of notes",
)
@click.option(
    "--velocity",
    prompt="Base velocity",
    default=110,
    show_default=True,
    type=int,
    help="Starting MIDI velocity 1–127",
)
@click.option(
    "--vel-decay-exp",
    prompt="Velocity decay exponent",
    default=0.15,
    show_default=True,
    type=float,
    help="Velocity decay per step",
)
def generate(bpm, note, start_len, factor, num_notes, velocity, vel_decay_exp):
    """Generate a stutter pattern MIDI file."""
    notes_data = []
    pos = 0.0
    length = start_len

    for i in range(num_notes):
        if length < 0.02:
            break
        vel = max(30, round(velocity * (factor ** (i * vel_decay_exp))))
        notes_data.append((pos, length * 0.92, note, vel))
        pos += length
        length *= factor

    midi_bytes = make_midi(notes_data, tempo=bpm)

    out_dir = CONFIG["out_dir"]
    filename = f"stutter_bpm{bpm}_factor{factor}_velexp{vel_decay_exp}.mid"
    file_path = Path(out_dir) / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(midi_bytes)

    click.echo(f"\nMIDI written: {file_path}")
    click.echo(f"Notes: {len(notes_data)}")


if __name__ == "__main__":
    generate()
