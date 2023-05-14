import io
import logging
import os
import subprocess
import tempfile

import pyphen # type: ignore
import spacy
from aeneas.executetask import ExecuteTask # type: ignore
from aeneas.syncmap.fragment import SyncMapFragment # type: ignore
from aeneas.task import Task # type: ignore
from pydub import AudioSegment, silence # type: ignore

from backend.schemas import FragmentBase, ProcessedAudio, AudioReport, Clause
from backend.common import rescaled_noise

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")
# Initialize the Pyphen syllable counter with the desired language
dic = pyphen.Pyphen(lang='en')


def align_clause(audio_filepath: str, clause: Clause):
    """Align a transcript to an audio file.
    
    :param audio_filepath: The path to the audio file.
    :param transcript: The transcript to align.
    
    :return: The alignment.
    """
    with tempfile.NamedTemporaryFile(mode="w") as transcript_file:
        transcript_file.write(clause.text)
        transcript_file.flush()
        # create Task object
        config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=json"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = os.path.abspath(audio_filepath)
        task.text_file_path_absolute = os.path.abspath(transcript_file.name)
        ExecuteTask(task).execute()

        return task.sync_map_leaves()

def process_fragments(
    input: AudioSegment, 
    alignment: list[SyncMapFragment], 
    extend_silence_ms: int=500, 
    min_silence_ms: int=250, 
    noise_scale: float=0.1, 
    target_speech_rate: float=3.0, 
    shift_fragment_windows: int=-50,
    target_dbfs: int=-20,
) -> list[FragmentBase]:
    """Pad sections of silence in an audio file to be a certain length with additional
    length +/- the length as determined by the noise function.
    
    :param input: The input audio.
    :param alignment: Determines what rate to slow each segment (helps keep even speaking pace).
    :param extend_silence_ms: The desired silence extension length in milliseconds.
    :param min_silence_len: The threshold for detected silence length in milliseconds.
    :param noise_scale: The noise scale that determines the range of silence extension.
    :param target_speech_rate: The target speech rate in syllables per second.
    :param shift_fragment_windows: The number of milliseconds to shift the fragment window to avoid
        the ends being cutoff by inaccuracies in the forced alignmend algorithm.
    :param target_dbfs: The target decibels we want the average volume to be.

    :return: The output audio.
    """
    fragments = []
    for idx, fragment in enumerate(alignment):
        if fragment.is_head_or_tail:
            continue
        # The alignment timestamps tend to be a little off, so we shift the fragment
        #   window to avoid clicks at the end of each segment or cutting off the end
        #   of the segment.  If the previous ending fragment window was shifted, the
        #   beginning of the current fragment window will need to be shifted as well.
        fragment_start = max(0, int(fragment.begin * 1000) + shift_fragment_windows)
        fragment_end = int(fragment.end * 1000) + shift_fragment_windows
        raw_segment = input[fragment_start:fragment_end]

        # Translate the noise value to a range of 0.5 to 1.5 since the noise function
        #   returns a value between 0 and 1 and we want to scale up or down the
        #   extend_silence_ms value
        noise_factor = 1 + (rescaled_noise(idx, 1, noise_scale) - 0.5)
        nonsilent = silence.detect_nonsilent(raw_segment, min_silence_ms, -70)[0]
        nonsilent_segment = raw_segment[nonsilent[0]:nonsilent[1]]
        # Normalize gain across segments by boosting the difference between 
        #   the segments dBFS (average gain) and the target dBFS
        nonsilent_segment = nonsilent_segment.apply_gain(target_dbfs - nonsilent_segment.dBFS)

        # Export the 'segment' AudioSegment to a bytes object
        nonsilent_segment_data = nonsilent_segment.export(format="wav")
        words = nlp(fragment.text)
        syllable_count = sum([len(dic.positions(token.text)) + 1 for token in words])
        speech_rate = syllable_count / (len(nonsilent_segment) / 1000)
        retime_pct = max(-30, int(((target_speech_rate - speech_rate) / speech_rate) * 100))
        logger.debug(
            f"segment {idx}: speech rate {speech_rate:.2f} syllables per second,"
            f"  retiming by {retime_pct}%"
        )
        # Run SoundStretch with stdin and stdout
        soundstretch_process = subprocess.Popen(
            ["SoundStretch", "stdin", "stdout", f"-tempo={retime_pct}", "-speech"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        processed_data, _ = soundstretch_process.communicate(input=nonsilent_segment_data.read())
        
        # Convert the processed data back to an AudioSegment
        processed_segment = AudioSegment.from_file(io.BytesIO(processed_data))
        # Remove the last 25ms of the segment to avoid clicks
        processed_segment = processed_segment[:len(processed_segment) - 25]

        random_silence_duration = max(0, extend_silence_ms * noise_factor)
        logger.debug(
            f"segment {idx}: using noise value of {noise_factor:.4f}"
            f" to add {random_silence_duration}ms of silence"
        )
        extended_segment = processed_segment + AudioSegment.silent(duration=random_silence_duration)

        fragments.append(FragmentBase(
            processed_audio=ProcessedAudio(
                raw=raw_segment,
                nonsilent=nonsilent_segment,
                processed=processed_segment,
                extended=extended_segment
            ),
            report=AudioReport(
                speech_rate=speech_rate,
                retime_pct=retime_pct,
                noise_factor=noise_factor,
                raw_length=len(raw_segment),
                nonsilent_length=len(nonsilent_segment),
                silent_length=len(raw_segment) - len(nonsilent_segment),
                extended_length=len(extended_segment),
                random_silence_duration=random_silence_duration
            ),
            text=fragment.text,
        ))
    return fragments
