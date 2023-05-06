from typing import List, Tuple, Optional
import os

import noise

def list_directories(path: str) -> List[str]:
    dirs = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                dirs.append(entry.path)
    return dirs

def find_files_in_directories(directories: List[str], file_name: Optional[str]=None) -> List[str]:
    found_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file_name and file_name != file:
                    continue
                found_files.append(os.path.join(root, file))
    return found_files

def rescaled_noise(x, y, scale):
    noise_value = noise.snoise2(x * scale, y * scale)
    return (noise_value + 1) / 2
