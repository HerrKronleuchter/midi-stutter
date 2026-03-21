import click
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from pathlib import Path
from config import CONFIG


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
    ticks_per_beat = 480

    # Build note list
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

    # Convert to absolute tick events, then sort
    events = []
    for pos, length, pitch, vel in notes_data:
        on_tick = round(pos * ticks_per_beat)
        off_tick = round((pos + length) * ticks_per_beat)
        events.append((on_tick, "on", pitch, vel))
        events.append((off_tick, "off", pitch, 0))
    events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

    # Build MIDI file
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
    track.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))

    prev_tick = 0
    for tick, kind, pitch, vel in events:
        delta = tick - prev_tick
        prev_tick = tick
        if kind == "on":
            track.append(Message("note_on", note=pitch, velocity=vel, time=delta))
        else:
            track.append(Message("note_off", note=pitch, velocity=0, time=delta))

    # Save
    out_dir = Path(CONFIG["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"stutter_bpm{bpm}_factor{factor}_velexp{vel_decay_exp}.mid"
    mid.save(file_path)

    click.echo(f"\nMIDI written: {file_path}")
    click.echo(f"Notes: {len(notes_data)}")


if __name__ == "__main__":
    generate()
