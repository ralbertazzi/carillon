from dataclasses import dataclass


@dataclass(frozen=True)
class MusicBox:
    notes: list[str]
    pitch: float
    reverse: bool = False
