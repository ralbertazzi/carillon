import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import Union

from music21.chord import Chord
from music21.converter import parse
from music21.note import Note
from music21.stream import Measure, Part, Score, Voice


def note_for_carillon(note: str) -> str:
    """Convert flat notes (B-) in sharp notes (A#)."""
    if "-" not in note:
        return note

    octave = ["C", "D", "E", "F", "G", "A", "B"]
    note_below = octave[octave.index(note[0]) - 1]
    return f"{note_below}#{note[2]}"


@dataclass(frozen=True)
class ParsedNote:
    name_with_octave: str
    beat: float
    beat_duration: float


def parse_note_or_chord(note: Union[Note, Chord]) -> list[ParsedNote]:
    if isinstance(note, Note):
        return [
            ParsedNote(
                name_with_octave=note.nameWithOctave,
                beat=note.beat,
                beat_duration=note.beatDuration.quarterLength,
            )
        ]
    else:
        chord = note
        return [
            ParsedNote(
                name_with_octave=note.nameWithOctave,
                beat=chord.beat,
                beat_duration=chord.beatDuration.quarterLength,
            )
            for note in chord.notes
        ]


def parse_voice_or_measure(voice: Union[Measure, Voice]) -> list[ParsedNote]:
    return list(
        note
        for note_or_chord in voice.notes
        for note in parse_note_or_chord(note_or_chord)
    )


def get_notes_from_measure(measure: Measure) -> list[ParsedNote]:
    voices = list(measure.voices)
    if not voices:
        return parse_voice_or_measure(measure)
    else:
        # Get notes from multiple voices: https://musescore.org/en/handbook/voices
        return list(
            itertools.chain.from_iterable(
                parse_voice_or_measure(voice) for voice in voices
            )
        )


def get_score_from_file(filename: str, carillon_beat: int) -> dict[int, set[str]]:
    result: dict[int, set[str]] = defaultdict(set)

    score: Score = parse(filename)
    parts: list[Part] = list(score.parts)

    for part in parts:
        assert part.hasMeasures()

        # TODO: where to I get the end measure?
        measures: list[Measure] = list(part.measures(1, 32))[1:]
        for measure_idx, measure in enumerate(measures, start=0):
            notes = get_notes_from_measure(measure)
            for note in notes:
                note_idx_in_measure = int(
                    (note.beat - 1) / (note.beat_duration * 4) * carillon_beat
                )
                note_idx_in_score = note_idx_in_measure + measure_idx * carillon_beat
                result[note_idx_in_score].add(note_for_carillon(note.name_with_octave))

    return dict(result)
