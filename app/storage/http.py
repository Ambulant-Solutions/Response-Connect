from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from werkzeug.http import dump_options_header


_STREAM_CHUNK_SIZE = 1024 * 1024


def iter_s3_body(
    body: Any,
    *,
    chunk_size: int = _STREAM_CHUNK_SIZE,
) -> Iterator[bytes]:
    """
    Yield chunks from a botocore StreamingBody and always close it.
    """

    try:
        while True:
            chunk = body.read(chunk_size)

            if not chunk:
                break

            yield chunk

    finally:
        body.close()

def build_content_disposition(
    filename: str,
    *,
    inline: bool = False,
) -> str:
    disposition = "inline" if inline else "attachment"

    safe_filename = (
        filename
        .replace("\\", "_")
        .replace("/", "_")
        .replace("\r", "")
        .replace("\n", "")
        .replace('"', "")
        .strip()
    )

    if not safe_filename:
        safe_filename = "download"

    return dump_options_header(
        disposition,
        {
            "filename": safe_filename,
        },
    )