"""CSV serialization has no file or network access."""

import csv
import io


def render_csv(values: list[int]) -> str:
    """Serialize bounded numeric rows with a fixed, non-formula header."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["value"])
    writer.writerows([value] for value in values)
    return output.getvalue()
