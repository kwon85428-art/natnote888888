"""Collect DB-referenced upload paths and detect orphan files under upload_dir."""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Article, PlatformSettings, Site

_UPLOADS_IN_TEXT_RE = re.compile(r"/uploads/([^)\"'\s<>]+)", re.IGNORECASE)


def normalize_upload_relpath(raw: str | None) -> str | None:
    if raw is None:
        return None
    p = str(raw).strip().replace("\\", "/")
    if not p:
        return None
    if p.startswith(("http://", "https://")):
        return None
    if "/uploads/" in p:
        p = p.rsplit("/uploads/", 1)[-1]
    elif p.startswith("/uploads/"):
        p = p[len("/uploads/") :]
    elif p.lower().startswith("uploads/"):
        p = p[8:]
    p = p.lstrip("/")
    if not p or ".." in Path(p).parts:
        return None
    return p.replace("\\", "/")


def _add_text_refs(refs: set[str], text: str | None) -> None:
    if not text:
        return
    for m in _UPLOADS_IN_TEXT_RE.finditer(text):
        rel = normalize_upload_relpath(m.group(1))
        if rel:
            refs.add(rel)


def collect_referenced_relpaths(db: Session) -> set[str]:
    refs: set[str] = set()

    for logo_path, in db.query(PlatformSettings.logo_path).all():
        rel = normalize_upload_relpath(logo_path)
        if rel:
            refs.add(rel)

    for favicon_path, logo_path in db.query(Site.favicon_path, Site.logo_path).all():
        for p in (favicon_path, logo_path):
            rel = normalize_upload_relpath(p)
            if rel:
                refs.add(rel)

    for cover_path, body_markdown, body_html in db.query(
        Article.cover_path,
        Article.body_markdown,
        Article.body_html,
    ).all():
        rel = normalize_upload_relpath(cover_path)
        if rel:
            refs.add(rel)
        _add_text_refs(refs, body_markdown)
        _add_text_refs(refs, body_html)

    return refs


def _is_safe_under_upload_root(upload_root: Path, file_path: Path) -> bool:
    try:
        root = upload_root.resolve()
        resolved = file_path.resolve()
        return resolved.is_file() and resolved.is_relative_to(root)
    except OSError:
        return False


def iter_orphan_file_paths(upload_root: Path, refs: set[str]) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    if not upload_root.is_dir():
        return out
    for path in upload_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if not _is_safe_under_upload_root(upload_root, path):
            continue
        try:
            rel = path.relative_to(upload_root).as_posix()
        except ValueError:
            continue
        if rel not in refs:
            out.append((rel, path))
    out.sort(key=lambda x: x[0])
    return out


def prune_orphan_uploads(db: Session, *, execute: bool = False) -> dict:
    refs = collect_referenced_relpaths(db)
    pairs = iter_orphan_file_paths(settings.upload_dir, refs)
    total_b = 0
    for _rel, p in pairs:
        try:
            total_b += p.stat().st_size
        except OSError:
            pass
    sample = [rel for rel, _ in pairs[:80]]
    out: dict = {
        "dry_run": not execute,
        "orphan_count": len(pairs),
        "total_bytes": total_b,
        "sample_paths": sample,
        "deleted_count": 0,
        "freed_bytes": 0,
    }
    if not execute or not pairs:
        return out

    deleted = 0
    freed = 0
    deleted_sample: list[str] = []
    for rel, p in pairs:
        if not _is_safe_under_upload_root(settings.upload_dir, p):
            continue
        try:
            sz = p.stat().st_size
            p.unlink()
            deleted += 1
            freed += sz
            if len(deleted_sample) < 80:
                deleted_sample.append(rel)
        except OSError:
            continue
    out["deleted_count"] = deleted
    out["freed_bytes"] = freed
    out["sample_paths"] = deleted_sample
    return out
