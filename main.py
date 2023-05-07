import os
import json
from subprocess import run
from functools import partial

from pydub import AudioSegment

from common import list_directories, find_files_in_directory
from fetch_audio import fetch
from process_audio import process_segments, align_transcript


def main():
    for script_file in find_files_in_directory("scripts", "\.json"):
        dir = partial(os.path.join)
        audio_dir = partial(dir, "audio")
        raw_dir = audio_dir("raw")
        with open(script_file, "r") as script_file:
            script = json.load(script_file)
        fetch("Sleepy Sister", script, raw_dir)
        # initialize directories
        retimed_dir = audio_dir("retimed")
        os.makedirs(retimed_dir, exist_ok=True)
        for section_ix, section in enumerate(script):
            for clause_ix, clause in enumerate(section['clauses']):
                name = f"{section_ix}_{section['name']}_{clause_ix}.wav"
                retimed_file = audio_dir("retimed", name)
                input_file = dir(raw_dir, name)
                alignment = align_transcript(input_file, clause)
                # retime silence to consistent >1s, normalize gain, and slow down 15%
                audio = AudioSegment.from_file(input_file)
                output = process_segments(audio, alignment, 1000, 250, 100, 3)
                output.export(retimed_file, format="wav")

if __name__ == "__main__":
    main()
