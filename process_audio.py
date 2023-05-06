import logging

import click
from pydub import AudioSegment, silence

from utils import rescaled_noise

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def pad_silence(input_file: str, output_file: str, extend_silence_ms: int, min_silence_ms: int, noise_scale: int):
    """Pad sections of silence in an audio file to be a certain length with additional
    length +/- the length as determined by the noise function.
    
    :param input_file: The input audio file.
    :param output_file: The output audio file.
    :param extend_silence_ms: The desired silence extension length in milliseconds.
    :param min_silence_len: The threshold for detected silence length in milliseconds.
    :param noise_scale: The noise scale that determines the range of silence extension."""
    # Load the audio file (MP3 support added)
    audio = AudioSegment.from_file(input_file)

    # Detect silence
    silence_thresh = -50
    silent_segments = silence.split_on_silence(audio, min_silence_ms, silence_thresh, keep_silence=True)

    # Extend silence
    extended_audio = AudioSegment.empty()

    for idx, segment in enumerate(silent_segments):
        noise_value = 1 + (rescaled_noise(idx, 1, noise_scale) - 0.5)
        nonsilent = silence.detect_nonsilent(segment, min_silence_ms, silence_thresh)[0]
        silence_len = len(segment) - (nonsilent[1] - nonsilent[0])
        random_silence_duration = max(0, (extend_silence_ms - silence_len) * noise_value)
        logger.debug(f"silent segment {idx}: using noise value of {noise_value} to add {random_silence_duration}ms to original {silence_len}ms of silence")
        extended_audio += segment + AudioSegment.silent(duration=random_silence_duration)

    # Export the modified audio
    extended_audio.export(output_file, format="wav")

@click.command(name='pad_silence')
@click.option('--input_file', default='input.mp3', help='Input audio file name (e.g., input.mp3).')
@click.option('--output_file', default='output.wav', help='Output audio file name (e.g., output.wav).')
@click.option('--extend_silence_ms', default=1000, help='Desired silence extension length in milliseconds.')
@click.option('--min_silence_ms', default=250, help='Detected silence length in milliseconds.')
@click.option('--noise_scale', default=100, help='Perlin noise scale factor.')
def pad_silence_command(input_file, output_file, extend_silence_ms, min_silence_ms, noise_scale):
    pad_silence(input_file, output_file, extend_silence_ms, min_silence_ms, noise_scale)

if __name__ == '__main__':
    pad_silence()