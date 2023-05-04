import logging

import click
from pydub import AudioSegment, silence
from noise import pnoise1
import numpy as np

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.command()
@click.option('--input_file', default='input.mp3', help='Input audio file name (e.g., input.mp3).')
@click.option('--output_file', default='output.wav', help='Output audio file name (e.g., output.wav).')
@click.option('--extend_silence_ms', default=1000, help='Desired silence extension length in milliseconds.')
@click.option('--min_silence_len', default=250, help='Detected silence length in milliseconds.')
@click.option('--noise_scale', default=100, help='Perlin noise scale factor.')
def extend_silence(input_file: str, output_file: str, extend_silence_ms: int, min_silence_len: int, noise_scale: int):
    # Load the audio file (MP3 support added)
    audio = AudioSegment.from_file(input_file)

    # Detect silence
    silence_thresh = -50
    silent_segments = silence.split_on_silence(audio, min_silence_len, silence_thresh, keep_silence=True)

    # Extend silence
    extended_audio = AudioSegment.empty()

    for idx, segment in enumerate(silent_segments):
        noise_value = (pnoise1(idx / float(noise_scale), 1) + 1) / 2
        random_silence_duration = int(extend_silence_ms * noise_value)
        logger.debug(f"silent segment {idx}: using noise value of {noise_value} to add {random_silence_duration}ms")
        extended_audio += segment + AudioSegment.silent(duration=random_silence_duration)

    # Export the modified audio
    extended_audio.export(output_file, format="wav")

if __name__ == '__main__':
    extend_silence()