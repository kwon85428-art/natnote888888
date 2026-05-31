"""scrape 元数据解析与限流读取（无需外网）。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.scrape import HEAD_SCAN_BYTES, _parse_html_metadata, _read_html_head_bytes


async def _fake_response(chunks: list[bytes]) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/")
    response = httpx.Response(200, request=request)
    response._content = b"".join(chunks)
    return response


async def test_read_html_head_bytes_stops_at_head_end() -> None:
    html = b"<html><head><title>T</title></head><body>" + b"x" * 5000
    resp = await _fake_response([html])

    async def aiter_bytes(_size: int):
        yield html

    resp.aiter_bytes = aiter_bytes  # type: ignore[method-assign]
    out = await _read_html_head_bytes(resp, max_bytes=HEAD_SCAN_BYTES)
    assert b"</head>" in out.lower()
    assert len(out) < len(html)


async def test_read_html_head_bytes_respects_max_bytes() -> None:
    big = b"<html><head>" + b"x" * (HEAD_SCAN_BYTES + 4096)
    resp = await _fake_response([big])

    async def aiter_bytes(_size: int):
        yield big

    resp.aiter_bytes = aiter_bytes  # type: ignore[method-assign]
    out = await _read_html_head_bytes(resp, max_bytes=1024)
    assert len(out) <= 1024


def test_parse_html_metadata_title_and_description() -> None:
    html = """<!DOCTYPE html><html><head>
    <title>Example Site</title>
    <meta name="description" content="Short desc">
    <link rel="icon" href="/favicon.ico">
    </head><body></body></html>"""
    meta = _parse_html_metadata(html, "https://example.com/page")
    assert meta["title"] == "Example Site"
    assert meta["description"] == "Short desc"
    assert meta["favicon_url"].endswith("/favicon.ico")
    assert meta["resolved_url"] == "https://example.com/page"


def main() -> None:
    asyncio.run(test_read_html_head_bytes_stops_at_head_end())
    asyncio.run(test_read_html_head_bytes_respects_max_bytes())
    test_parse_html_metadata_title_and_description()
    print("test_scrape: ok")


if __name__ == "__main__":
    main()
