import math
from typing import Optional

import svgwrite


def _mm(val) -> str:
    return f"{val}mm"


def _line(
    dwg: svgwrite.Drawing, c1: tuple[float, float], c2: tuple[float, float]
) -> None:
    """Draw a line given its two extremes (x1, y1) and (x2, y2)."""
    dwg.add(
        dwg.line(
            (_mm(c1[0]), _mm(c1[1])),
            (_mm(c2[0]), _mm(c2[1])),
            stroke=svgwrite.rgb(0, 0, 0, "%"),
            stroke_width=".1mm",
        )
    )


def _cross(dwg: svgwrite.Drawing, size: float, x: float, y: float) -> None:
    hs = size / 2.0
    _line(dwg=dwg, c1=(x - hs, y), c2=(x + hs, y))
    _line(dwg=dwg, c1=(x, y - hs), c2=(x, y + hs))


def _draw_crosses(
    dwg: svgwrite.Drawing,
    line_offset: float,
    marker_size: float,
    marker_offset: float,
    margin: float,
    stave_width: float,
    stave_height: float,
) -> None:
    mark_top = marker_offset
    mark_btm = marker_offset

    centers = [
        (margin + stave_width, line_offset - mark_top),
        (margin + stave_width, line_offset + stave_height - margin + mark_btm),
        (margin, line_offset + stave_height - margin + mark_btm),
        (margin, line_offset - mark_top),
    ]

    for center in centers:
        _cross(dwg, marker_size, *center)

    _line(dwg, centers[0], centers[1])
    _line(dwg, centers[1], centers[2])
    _line(dwg, centers[2], centers[3])
    _line(dwg, centers[3], centers[0])


def _draw_stave_number(
    dwg: svgwrite.Drawing,
    font_size: float,
    line_offset: float,
    marker_offset: float,
    margin: float,
    stave_number: int,
    stave_height: float,
    title: str,
) -> None:
    dwg.add(
        dwg.text(
            f"STAVE {stave_number} - {title}",
            insert=(
                _mm(margin * 2),
                _mm(line_offset + stave_height - margin + marker_offset),
            ),
            fill="blue",
            font_size=_mm(font_size),
        )
    )


def _draw_music_box_notes(
    dwg: svgwrite.Drawing,
    font_size: float,
    line_offset: float,
    margin: float,
    stave_width: float,
    notes: list[str],
    pitch: float,
):
    for i, note in enumerate(notes):
        line_x = (i * pitch) + line_offset
        dwg.add(
            dwg.line(
                (_mm(margin), _mm(line_x)),
                (_mm(stave_width + margin), _mm(line_x)),
                stroke=svgwrite.rgb(0, 0, 0, "%"),
                stroke_width=".1mm",
            )
        )
        dwg.add(
            dwg.text(
                note,
                insert=(_mm(-2 + margin), _mm(line_x + font_size / 2)),
                fill="red",
                font_size=_mm(font_size),
            )
        )


_A4_WIDTH = 297.0
_A4_HEIGHT = 210.0


def create_staves(
    score: dict[int, set[str]],
    output: str,
    notes: list[str],
    title: Optional[str] = None,
    divisor: float = 4.0,
    font_size: float = 1.5,
    marker_offset: float = 6.0,
    marker_size: float = 5.0,
    margin: float = 20.0,
    page_width: float = _A4_WIDTH,
    page_height: float = _A4_HEIGHT,
    pitch: float = 2.0,
    pitch_offset: int = 1,
) -> None:
    """
    Prints a music score into one or more SVG files ready to be printed.
    Adapted from https://github.com/psav/punchbox.
    :param score: the score to print. It contains 0 or more notes for each time offset (zero based).
        Each offset will be equally spaced and the distance is specified by the 'divisor' parameter.
        Notes (such as C4, F#5, ..) must be contained in the music box notes (the 'notes' parameter).
    :param output: the output filename prefix for the SVG file(s) being generated.
    :param notes: the notes of the carillon, ordered from lowest to highest.
    :param title: the title of the song, printed on each stave. If not passed, the output filename is used.
    :param marker_offset: the upper and lower vertical offset (in mm) from the top and bottom lines to
            the borders of the stave (where you need to cut).
    :param marker_size: the size (in mm) of the marker placed on the four corners around a stave (cutting corners)
    :param margin: the horizontal and vertical margin (in mm) to be used. It's the distance between
            the borders of the page and the score.
    :param divisor: the distance (in mm) between consecutive notes (perpendicular to the pitch)
    :param font_size: the font size used to print titles and notes.
    :param page_width: the width (in mm) of the page used to print the score.
    :param page_height: the height (in mm) of the page used to print the score.
    :param pitch: the distances (in mm) between two consecutive lines of the score.
    :param pitch_offset: the offset (in number of pitches) at which the score has to start.
    """
    max_time = max(score)
    score_length = (max_time + pitch_offset) * divisor
    print(f"SCORE LENGTH: {score_length}")

    stave_height = (len(notes) - 1) * pitch + margin
    staves_per_page = int(math.floor((page_height - margin * 2) / stave_height))
    if staves_per_page <= 0:
        raise ValueError(
            "There is not enough space to print one stave in a page. "
            "Please increase the page height or decrease some of the following: margin, pitch."
        )

    stave_width: float = page_width - (margin * 2)
    print(f"STAVE WIDTH: {stave_width} - HEIGHT: {stave_height}")
    num_staves_required = int(math.ceil(score_length / stave_width))
    print(f"NUM STAVES: {num_staves_required}")

    pages = int(math.ceil(num_staves_required / staves_per_page))
    print(f"PAGES: {pages}")

    offset = pitch_offset
    for page in range(pages):
        print(f"Writing page {page}...")

        dwg = svgwrite.Drawing(
            f"{output}_{page}.svg", size=(_mm(page_width), _mm(page_height))
        )

        for stave in range(staves_per_page):
            line_offset = stave * stave_height + margin

            _draw_crosses(
                dwg=dwg,
                line_offset=line_offset,
                marker_size=marker_size,
                marker_offset=marker_offset,
                margin=margin,
                stave_width=stave_width,
                stave_height=stave_height,
            )

            _draw_stave_number(
                dwg=dwg,
                font_size=font_size,
                line_offset=line_offset,
                margin=margin,
                marker_offset=marker_offset,
                stave_number=(page * staves_per_page) + stave,
                stave_height=stave_height,
                title=title or output,
            )

            _draw_music_box_notes(
                dwg=dwg,
                font_size=font_size,
                line_offset=line_offset,
                margin=margin,
                stave_width=stave_width,
                notes=notes,
                pitch=pitch,
            )

            offset_width = ((page * staves_per_page) + stave) * stave_width

            while True:
                note_width = offset * divisor - offset_width
                if note_width > stave_width:
                    break

                for note in score.get(offset - pitch_offset, set()):
                    note_pos = notes.index(note)

                    dwg.add(
                        dwg.circle(
                            (
                                _mm(note_width + margin),
                                _mm((note_pos * pitch) + line_offset),
                            ),
                            "1mm",
                            fill="black",
                        )
                    )

                offset += 1

        dwg.save()
