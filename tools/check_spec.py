#!/usr/bin/env python3
"""Validate PrismShare specification structure and canonical vector integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_DOCS = (
    "FORMAT.md",
    "DECODER.md",
    "BIT-LOADING.md",
    "APHOTIC.md",
    "STREAM.md",
    "BRANDING.md",
)
MIRROR_DOCS = (
    "README.md",
    "FORMAT.md",
    "DECODER.md",
    "BIT-LOADING.md",
    "APHOTIC.md",
    "STREAM.md",
    "BRANDING.md",
    "GLOSSARY.md",
    "VERSIONING.md",
    "CONFORMANCE.md",
    "VALIDATION.md",
    "SECURITY.md",
    "EXAMPLES.md",
    "CHANGELOG.md",
)
LINK_RE = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: {exc}")


def check_status_banners() -> None:
    for name in STATUS_DOCS:
        text = (ROOT / name).read_text(encoding="utf-8")
        if "Document status" not in text[:1600]:
            fail(f"{name}: missing top-of-document status banner")


def check_local_links() -> None:
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                fail(f"{path.relative_to(ROOT)}: broken local link {raw!r}")


def check_manifest() -> None:
    vector_dir = ROOT / "vectors"
    manifest = load_json(vector_dir / "manifest.json")
    if manifest.get("manifestVersion") != 1:
        fail("vectors/manifest.json: unsupported manifestVersion")
    listed: set[str] = set()
    for entry in manifest.get("files", []):
        rel = entry.get("path")
        if not isinstance(rel, str) or rel in listed:
            fail("vectors/manifest.json: missing or duplicate path")
        listed.add(rel)
        path = vector_dir / rel
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry.get("sha256"):
            fail(f"vectors/{rel}: SHA-256 mismatch; got {digest}")
        data = load_json(path)
        if data.get("status") != entry.get("status"):
            fail(f"vectors/{rel}: status disagrees with manifest")
    actual = {p.name for p in vector_dir.glob("*.json") if p.name != "manifest.json"}
    if listed != actual:
        fail(f"vectors/manifest.json: listed={sorted(listed)}, actual={sorted(actual)}")


def decode_hex(value: object, label: str) -> bytes:
    if not isinstance(value, str) or len(value) % 2 or not re.fullmatch(r"[0-9a-f]*", value):
        fail(f"{label}: hex must be lowercase, even-length hexadecimal")
    return bytes.fromhex(value)


def check_aphotic_vectors() -> None:
    data = load_json(ROOT / "vectors" / "aphotic-fountain-v1.json")
    source = data["source"]
    expected_length = 13 + source["chunkSize"]
    for index, value in data["pagePayloadHex"].items():
        page = decode_hex(value, f"Aphotic page {index}")
        if len(page) != expected_length or page[:2] != b"PS":
            fail(f"Aphotic page {index}: wrong length or magic")
        if int.from_bytes(page[2:4], "big") != source["transferId"]:
            fail(f"Aphotic page {index}: wrong transfer id")
        if int.from_bytes(page[4:6], "big") != int(index):
            fail(f"Aphotic page {index}: header index disagrees with vector key")
        if int.from_bytes(page[6:8], "big") != source["dataPages"] or page[8] != 0xFF:
            fail(f"Aphotic page {index}: wrong dataPages or repair mode")
        if int.from_bytes(page[9:13], "big") != source["length"]:
            fail(f"Aphotic page {index}: wrong total length")


def check_stream_vectors() -> None:
    data = load_json(ROOT / "vectors" / "stream-v1.json")
    codecs = {0: 13, 8: 7, 9: 4}
    for case in data["positive"]:
        frame = decode_hex(case["hex"], f"Stream positive {case['id']}")
        if len(frame) < 10 or frame[:3] != b"PV\x01":
            fail(f"Stream positive {case['id']}: wrong header")
        codec = frame[5] >> 4
        count = frame[9]
        if codec not in codecs or not 1 <= count <= 200:
            fail(f"Stream positive {case['id']}: invalid codec or count")
        if len(frame) != 10 + count * codecs[codec]:
            fail(f"Stream positive {case['id']}: exact length failure")
        packets = [frame[10 + i * codecs[codec] : 10 + (i + 1) * codecs[codec]] for i in range(count)]
        if codec == 0 and any(packet[0] != 0x04 for packet in packets):
            fail(f"Stream positive {case['id']}: invalid AMR TOC")
        if codec in (8, 9) and any(packet[-1] & 0x0F for packet in packets):
            fail(f"Stream positive {case['id']}: non-zero Codec2 padding")
    for case in data["negative"]:
        decode_hex(case["hex"], f"Stream negative {case['id']}")
        if case.get("disposition") not in {"reject", "ignore", "not-this-protocol"}:
            fail(f"Stream negative {case['id']}: invalid disposition")


def check_mirror(mirror: Path) -> None:
    for name in MIRROR_DOCS:
        source = ROOT / name
        target = mirror / name
        if not target.exists():
            fail(f"mirror missing {name}")
        if source.read_text(encoding="utf-8") != target.read_text(encoding="utf-8"):
            fail(f"mirror differs for {name}")
    for name in ("README.md", "manifest.json", "aphotic-fountain-v1.json", "stream-v1.json", "symbol-vectors-v1.json"):
        source = ROOT / "vectors" / name
        target = mirror / "vectors" / name
        if not target.exists() or source.read_text(encoding="utf-8") != target.read_text(encoding="utf-8"):
            fail(f"mirror differs for vectors/{name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mirror", type=Path, help="path to an implementation docs mirror")
    args = parser.parse_args()
    try:
        check_status_banners()
        check_local_links()
        check_manifest()
        check_aphotic_vectors()
        check_stream_vectors()
        if args.mirror:
            check_mirror(args.mirror.resolve())
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"spec check failed: {exc}", file=sys.stderr)
        return 1
    print("PrismShare specification checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
