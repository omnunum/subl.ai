from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class ProcessedAudio(BaseModel):
    raw: str
    nonsilent: str
    processed: str
    extended: str

class AudioReport(BaseModel):
    speech_rate: float
    retime_pct: int
    noise_factor: float
    raw_length: int
    nonsilent_length: int
    silent_length: int
    extended_length: int
    random_silence_duration: int


class FragmentBase(BaseModel):
    processed_audio: Optional[ProcessedAudio]
    report: Optional[AudioReport]
    text: Optional[str]

class FragmentInsert(FragmentBase):
    text: str

class FragmentUpdate(FragmentBase):
    pass

class Fragment(FragmentBase):
    id: UUID
    text: str


class ClauseBase(BaseModel):
    audio: Optional[str]
    fragments: Optional[list[Fragment]]

    @property
    def text(self):
        return "\n".join([f.text for f in self.fragments])

class ClauseInsert(ClauseBase):
    fragments: list[Fragment]

class ClauseUpdate(ClauseBase):
    pass

class Clause(ClauseBase):
    id: UUID
    fragments: list[Fragment]



class SectionBase(BaseModel):
    name: Optional[str]
    audio: Optional[str]
    clauses: Optional[list[Clause]]

class SectionInsert(SectionBase):
    name: str
    clauses: list[Clause]

class SectionUpdate(SectionBase):
    pass

class Section(SectionBase):
    id: UUID
    clauses: list[Clause]
    name: str


class ScriptBase(BaseModel):
    name: Optional[str]
    sections: Optional[list[Section]]

class ScriptInsert(ScriptBase):
    name: str
    sections: list[Section]

class ScriptUpdate(ScriptBase):
    pass

class Script(ScriptBase):
    id: UUID
    sections: list[Section]
    name: str