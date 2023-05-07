import io
import logging
import subprocess
import os
import tempfile

from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.syncmap.fragment import SyncMapFragment
from pydub import AudioSegment, silence


from common import rescaled_noise, Clause

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def align_transcript(audio_filepath: str, transcript: Clause):
    """Align a transcript to an audio file.
    
    :param audio_filepath: The path to the audio file.
    :param transcript: The transcript to align.
    
    :return: The alignment.
    """
    with tempfile.NamedTemporaryFile(mode="w") as transcript_file:
        transcript_file.write("\n".join(transcript))
        transcript_file.flush()
        # create Task object
        config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=json"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = os.path.abspath(audio_filepath)
        task.text_file_path_absolute = os.path.abspath(transcript_file.name)
        ExecuteTask(task).execute()

        return task.sync_map_leaves()

def process_segments(input: AudioSegment, alignment: list[SyncMapFragment], extend_silence_ms: int, min_silence_ms: int, noise_scale: int, target_speech_rate: float) -> AudioSegment:
    """Pad sections of silence in an audio file to be a certain length with additional
    length +/- the length as determined by the noise function.
    
    :param input: The input audio.
    :param transcript: Determines what rate to slow each segment (helps keep even speaking pace).
    :param extend_silence_ms: The desired silence extension length in milliseconds.
    :param min_silence_len: The threshold for detected silence length in milliseconds.
    :param noise_scale: The noise scale that determines the range of silence extension.
    
    :return: The output audio.
    """
    
    # Extend silence
    extended_audio = AudioSegment.empty()
    for idx, fragment in enumerate(alignment):
        if fragment.is_head_or_tail:
            continue
        segment = input[float(fragment.begin) * 1000:float(fragment.end) * 1000]

        # used to debug individual segments
        # os.makedirs("audio/fragments", exist_ok=True)
        # segment.export(f"audio/fragments/{idx}_raw.wav", format="wav")

        noise_value = 1 + (rescaled_noise(idx, 1, noise_scale) - 0.5)
        nonsilent = silence.detect_nonsilent(segment, min_silence_ms, -50)[0]
        nonsilent_len = nonsilent[1] - nonsilent[0]
        silence_len = len(segment) - nonsilent_len
        random_silence_duration = max(0, (extend_silence_ms - silence_len) * noise_value)
        logger.debug(
            f"segment {idx}: using noise value of {noise_value:.4f}"
            f"to add {random_silence_duration}ms to original {silence_len}ms of silence"
        )
        # Normalize gain by removing headroom
        segment = segment.apply_gain(-20 - segment.dBFS)

        # Export the 'segment' AudioSegment to a bytes object
        segment_data = segment.export(format="wav")

        word_count = len(fragment.text.split())
        speech_rate = word_count / (nonsilent_len / 1000)
        retime_pct = int(((target_speech_rate - speech_rate) / speech_rate) * 100)
        logger.debug(
            f"segment {idx}: speech rate {speech_rate:.2f} words per second,"
            f"retiming by {retime_pct}%"
        )
        # Run SoundStretch with stdin and stdout
        soundstretch_process = subprocess.Popen(
            ["SoundStretch", "stdin", "stdout", f"-tempo={retime_pct}", "-speech"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        processed_data, _ = soundstretch_process.communicate(input=segment_data.read())
        
        # Convert the processed data back to an AudioSegment
        processed_segment = AudioSegment.from_file(io.BytesIO(processed_data))
        # processed_segment.export(f"audio/fragments/{idx}_processed.wav", format="wav")
        
        extended_audio += processed_segment + AudioSegment.silent(duration=random_silence_duration)
        
    return extended_audio
