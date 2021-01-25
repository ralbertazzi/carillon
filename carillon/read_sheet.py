from collections import defaultdict

from music21.converter import parse
from music21.note import Note
from music21.stream import Measure, Part, Score


def note_for_carillon(note: str) -> str:
    if "-" not in note:
        return note

    octave = ["C", "D", "E", "F", "G", "A", "B"]
    note_below = octave[octave.index(note[0]) - 1]
    return f"{note_below}#{note[2]}"


def get_notes(measure: Measure) -> list[Note]:
    voices = list(measure.voices)
    if not voices:
        return list(measure.notes)
    else:
        # Get notes from multiple voices: https://musescore.org/en/handbook/voices
        return [note for voice in voices for note in list(voice.notes)]


def get_score_from_file(filename: str, carillon_beat: int) -> dict[int, set[str]]:
    result: dict[int, set[str]] = defaultdict(set)

    score: Score = parse(filename)
    parts: list[Part] = list(score.parts)

    for part in parts:
        assert part.hasMeasures()
        measures: list[Measure] = list(part.measures(1, 32))[
            1:
        ]  # TODO: where to I get the end measure?
        for measure_idx, measure in enumerate(measures, start=0):
            notes = get_notes(measure)
            for note in notes:
                note_idx_in_measure = int(
                    (note.beat - 1)
                    / (note.beatDuration.quarterLength * 4)
                    * carillon_beat
                )
                note_idx_in_score = note_idx_in_measure + measure_idx * carillon_beat
                result[note_idx_in_score].add(note_for_carillon(note.nameWithOctave))

    return dict(result)
