from carillon.read_sheet import get_score_from_file
from carillon.svg import create_staves

AVAILABLE_NOTES = [
    "F3",
    "G3",
    "C4",
    "D4",
    "E4",
    "F4",
    "G4",
    "A4",
    "A#4",
    "B4",
    "C5",
    "C#5",
    "D5",
    "D#5",
    "E5",
    "F5",
    "F#5",
    "G5",
    "G#5",
    "A5",
    "A#5",
    "B5",
    "C6",
    "C#6",
    "D6",
    "D#6",
    "E6",
    "F6",
    "G6",
    "A6",
]

assert len(set(AVAILABLE_NOTES)) == 30

if __name__ == "__main__":
    carillon_beat = 8
    filename = "/Users/ra/Documents/MuseScore3/Scores/Carillon_1.musicxml"
    score = get_score_from_file(filename=filename, carillon_beat=carillon_beat)

    create_staves(
        notes=AVAILABLE_NOTES,
        score=score,
        title="My Composition",
        output="composition",
    )
