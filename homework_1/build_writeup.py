"""Extract all markdown cells from 01_hw.ipynb starting at Task 1 and write them
to writeup.md. Pipe writeup.md through pandoc to produce hw1_writeup.pdf."""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
NB_PATH = HERE / "01_hw.ipynb"
OUT_MD = HERE / "writeup.md"


def main() -> None:
    nb = json.loads(NB_PATH.read_text())

    # find the cell whose source starts with '# Task 1'
    start = next(
        i
        for i, c in enumerate(nb["cells"])
        if c["cell_type"] == "markdown"
        and "".join(c["source"]).lstrip().startswith("# Task 1")
    )

    chunks: list[str] = [
        "# Homework 1 Write-up",
        "",
        "Written responses for Tasks 1–6, extracted from `01_hw.ipynb`.",
        "",
    ]

    for cell in nb["cells"][start:]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"]).strip()
        if not src:
            continue
        # drop raw HTML img tags — they don't render in PDF
        src = re.sub(r"<img[^>]*>", "", src)
        chunks.append(src)
        chunks.append("")  # blank line between cells

    OUT_MD.write_text("\n".join(chunks))
    print(f"wrote {OUT_MD} ({len(chunks)} blocks)")


if __name__ == "__main__":
    main()
