import os
import re
from pathlib import Path
from typing import Optional

import noise # type: ignore


def list_directories(path: str) -> list[Path]:
    dirs = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                dirs.append(Path(entry.path))
    return dirs

def find_files_in_directory(directory: str, regex: Optional[str]=None) -> list[Path]:
    found_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if regex and not re.search(regex, os.path.basename(file)):
                continue
            found_files.append(Path(root, file))
    return found_files

def rescaled_noise(x, y, scale):
    noise_value = noise.snoise2(x * scale, y * scale)
    return (noise_value + 1) / 2
