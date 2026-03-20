#!/usr/bin/env python3
"""Setup script to initialize configuration file"""
from pathlib import Path


def setup():
    """Create config.py with user-specified output directory"""
    default_out_path = "."
    user_input = input(
        f"Enter output directory for MIDI files (default: {default_out_path}): "
    ).strip()
    out_dir = user_input if user_input else default_out_path

    config_path = Path(__file__).parent / "config.py"
    config_content = f'''"""Configuration dictionary for MIDI generation"""
from pathlib import Path

CONFIG = {{
    "out_dir": Path("{out_dir}"),
}}

CONFIG["out_dir"].mkdir(parents=True, exist_ok=True)
'''
    with open(config_path, "w") as f:
        f.write(config_content)

    print(f"Config file created: {config_path}")
    print(f"Midi-Files will be stored in: {out_dir}")
    print("Filenames will be generated as: stutter_[tempo]_[factor].mid")


if __name__ == "__main__":
    setup()
