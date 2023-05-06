import os

from utils import list_directories, find_files_in_directories
from fetch_audio import fetch
from process_audio import pad_silence



def main():
    fetch("Sleepy Sister")
    for directory in list_directories("scripts"):
        raw_dir = os.path.join(directory, "raw")
        input_files = find_files_in_directories([raw_dir])
        processed_dir = os.path.join(directory, "respaced")
        os.makedirs(processed_dir, exist_ok=True)
        for input_file in input_files:
            _, name = os.path.split(input_file)
            output_file = os.path.join(processed_dir, name)
            pad_silence(input_file, output_file, 1000, 250, 100)

if __name__ == "__main__":
    main()
