from dataclasses import dataclass

from dataclasses_json import dataclass_json
from pydub import AudioSegment

ScriptClause = list[str]
@dataclass
class ScriptSection:
    name: str
    clauses: list[ScriptClause]

@dataclass_json
@dataclass
class Script:
    name: str
    sections: list[ScriptSection]

@dataclass
class RenderedAudio:
    raw: AudioSegment
    nonsilent: AudioSegment
    processed: AudioSegment
    extended: AudioSegment

@dataclass
class RenderedAudioReport:
    speech_rate: float
    retime_pct: int
    noise_factor: float
    raw_length: int
    nonsilent_length: int
    silent_length: int
    extended_length: int
    random_silence_duration: int

@dataclass
class Fragment:
    audio: RenderedAudio
    report: RenderedAudioReport
    text: str

@dataclass
class RenderedClause:
    audio: AudioSegment
    fragments: list[Fragment]

    @property
    def text(self):
        return "\n".join([fragment.text for fragment in self.fragments])

@dataclass
class RenderedSection:
    name: str
    audio: AudioSegment
    clauses: list[RenderedClause]