import math
from typing import Optional

import svgwrite

from carillon.musicbox import MusicBox


def mm(val) -> str:
    return f"{val}mm"


def cross(dwg: svgwrite.Drawing, size: float, x: float, y: float) -> None:
    hs = size / 2.0
    dwg.add(
        dwg.line(
            (mm(y - hs), mm(x)),
            (mm(y + hs), mm(x)),
            stroke=svgwrite.rgb(0, 0, 0, "%"),
            stroke_width=".1mm",
        )
    )
    dwg.add(
        dwg.line(
            (mm(y), mm(x - hs)),
            (mm(y), mm(x + hs)),
            stroke=svgwrite.rgb(0, 0, 0, "%"),
            stroke_width=".1mm",
        )
    )


def _draw_crosses(
    dwg: svgwrite.Drawing,
    line_offset: float,
    marker_size: float,
    marker_offset: float,
    margin: float,
    max_stave_length: float,
    stave_width: float,
) -> None:
    mark_top = float(marker_offset)
    mark_btm = float(marker_offset)

    cross(dwg, marker_size, line_offset - mark_top, margin + max_stave_length)
    cross(
        dwg,
        marker_size,
        line_offset + stave_width - margin + mark_btm,
        margin + max_stave_length,
    )
    cross(dwg, marker_size, line_offset - mark_top, margin)
    cross(dwg, marker_size, line_offset + stave_width - margin + mark_btm, margin)


def _draw_stave_number(
    dwg: svgwrite.Drawing,
    font_size: float,
    line_offset: float,
    marker_offset: float,
    margin: float,
    stave_number: int,
    stave_width: float,
    title: str,
) -> None:
    dwg.add(
        dwg.text(
            f"STAVE {stave_number} - {title}",
            insert=(
                mm(margin * 2),
                mm(line_offset + stave_width - margin + marker_offset),
            ),
            fill="blue",
            font_size=mm(font_size),
        )
    )


def _draw_music_box_notes(
    dwg: svgwrite.Drawing,
    font_size: float,
    line_offset: float,
    margin: float,
    max_stave_length: float,
    notes: list[str],
    pitch: float,
):
    for i, note in enumerate(notes):
        line_x = (i * pitch) + line_offset
        dwg.add(
            dwg.line(
                (mm(margin), mm(line_x)),
                (mm(max_stave_length + margin), mm(line_x)),
                stroke=svgwrite.rgb(0, 0, 0, "%"),
                stroke_width=".1mm",
            )
        )
        dwg.add(
            dwg.text(
                note,
                insert=(mm(-2 + margin), mm(line_x + font_size / 2)),
                fill="red",
                font_size=mm(font_size),
            )
        )


def create_staves(
    music_box: MusicBox,
    score: dict[int, set[str]],
    output: str,
    title: Optional[str] = None,
    marker_offset: float = 6.0,
    marker_size: float = 5.0,
    margin: float = 20.0,
    font_size: float = 1.0,
    divisor: float = 0.25,
    page_width: float = 297.0,
    page_height: float = 210.0,
) -> None:

    max_time = max(score)
    max_length = max_time / divisor
    print(f"MAX LENGTH: {max_length}")

    stave_width = (len(music_box.notes) - 1) * music_box.pitch + margin
    staves_per_page = int(math.floor((page_height - margin) / stave_width))

    max_stave_length: float = page_width - (margin * 2)
    print(f"MAX STAVE LENGTH: {max_stave_length}")
    num_staves_required = int(math.ceil(max_length / max_stave_length))
    print(f"NUM STAVES: {num_staves_required}")

    pages = int(math.ceil(float(num_staves_required) / staves_per_page))
    print(f"PAGES: {pages}")

    no_staves = 0
    offset = 0
    for page in range(pages):
        print(f"Writing page {page}...")

        dwg = svgwrite.Drawing(
            f"{output}_{page}.svg", size=(mm(page_width), mm(page_height))
        )

        for stave in range(staves_per_page):
            max_stave_time = (
                (page * staves_per_page) + stave
            ) * max_stave_length + max_stave_length
            offset_time = max_stave_time - max_stave_length
            if no_staves > num_staves_required:
                break

            line_offset = stave * stave_width + margin
            _draw_crosses(
                dwg=dwg,
                line_offset=line_offset,
                marker_size=marker_size,
                marker_offset=marker_offset,
                margin=margin,
                max_stave_length=max_stave_length,
                stave_width=stave_width,
            )

            _draw_stave_number(
                dwg=dwg,
                font_size=font_size,
                line_offset=line_offset,
                margin=margin,
                marker_offset=marker_offset,
                stave_number=(page * staves_per_page) + stave,
                stave_width=stave_width,
                title=title or output,
            )

            _draw_music_box_notes(
                dwg=dwg,
                font_size=font_size,
                line_offset=line_offset,
                margin=margin,
                max_stave_length=max_stave_length,
                notes=music_box.notes,
                pitch=music_box.pitch,
            )

            while True:
                note_time = (offset / divisor) - offset_time
                if note_time > max_stave_length:
                    break

                for note in score.get(offset, set()):
                    note_pos = music_box.notes.index(note)
                    fill = "black"

                    dwg.add(
                        dwg.circle(
                            (
                                mm(note_time + margin),
                                mm((note_pos * music_box.pitch) + line_offset),
                            ),
                            "1mm",
                            fill=fill,
                        )
                    )

                offset += 1

        dwg.save()
