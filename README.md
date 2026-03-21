# midi-stutter

This is my 1st open source project. Please be patient with me ^^
I used AI in some parts.

Generates MIDI clips with a stutter effect — each note is shorter and quieter than the last.

## Installation

### With Nix

```bash
nix develop
```

### Without Nix

```bash
python -m venv .venv
source .venv/bin/activate       # bash/zsh
source .venv/bin/activate.fish  # fish
pip install -e .
```

This registers `create-midi-stutter` as a command on your system.

## Usage

Run interactively — confirm or change each parameter:

```bash
create-midi-stutter
```

Or pass parameters directly as flags:

```bash
create-midi-stutter --bpm 140 --factor 0.91 --out-dir ~/midi
```

Show all options:

```bash
create-midi-stutter --help
```

The output directory is saved and reused on the next run.

## Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `--bpm` | 127 | Tempo in BPM |
| `--note` | 36 | MIDI note number (C1=36, C2=48, C4=60) |
| `--start-len` | 1.0 | Initial note length in beats |
| `--factor` | 0.94 | Length multiplier per step (0–1) |
| `--num-notes` | 128 | Max number of notes |
| `--velocity` | 110 | Starting MIDI velocity (1–127) |
| `--vel-decay-exp` | 0.15 | Velocity decay exponent per step |
| `--out-dir` | `.` | Output directory for MIDI files |
