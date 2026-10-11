#!/usr/bin/env python3
"""Verify this research archive offline without executing evidence or using auth."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import zipfile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(repository: Path, structural_only: bool) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    formats = json.loads((repository / "manifests/content-formats.json").read_text())
    special_formats = {item["path"]: item for item in formats["files"]}
    paths = [path for path in sorted(repository.rglob("*")) if path.is_file()
             and ".git" not in path.relative_to(repository).parts
             and "__pycache__" not in path.relative_to(repository).parts]

    def fail(path: Path, check: str, detail: str) -> None:
        errors.append({"path": str(path.relative_to(repository)), "check": check, "detail": detail})

    for path in paths:
        relative = str(path.relative_to(repository))
        special = special_formats.get(relative)
        try:
            if special and special["format"] == "intentional-invalid-json":
                if sha256(path) != special["sha256"]:
                    fail(path, "negative_fixture_hash", "fixture no longer matches the archived diagnostic input")
                try:
                    json.loads(path.read_text())
                    fail(path, "negative_fixture", "expected malformed JSON/encoding but input parsed")
                except (UnicodeDecodeError, json.JSONDecodeError):
                    counts["intentional_invalid_json_fixtures"] += 1
            elif special and special["format"] == "concatenated-json-values":
                text = path.read_text()
                decoder = json.JSONDecoder()
                index = 0
                while index < len(text):
                    if text[index].isspace():
                        index += 1
                        continue
                    _, index = decoder.raw_decode(text, index)
                    counts["concatenated_json_values"] += 1
                counts["concatenated_json_streams"] += 1
            elif path.suffix == ".json":
                json.loads(path.read_text())
                counts["json"] += 1
            elif path.suffix == ".jsonl":
                for index, line in enumerate(path.read_text().splitlines(), 1):
                    if line.strip():
                        try:
                            json.loads(line)
                            counts["jsonl_records"] += 1
                        except json.JSONDecodeError as exc:
                            fail(path, "jsonl", f"line {index}: {exc.msg}")
                counts["jsonl"] += 1
            elif path.suffix == ".py":
                ast.parse(path.read_text(), filename=str(path.relative_to(repository)))
                counts["python_syntax"] += 1
        except (UnicodeDecodeError, json.JSONDecodeError, SyntaxError) as exc:
            fail(path, "syntax", str(exc).splitlines()[0])

    authored_markdown = [repository / "README.md", repository / "THIRD_PARTY_NOTICES.md",
                         *sorted((repository / "docs").glob("*.md"))]
    for path in authored_markdown:
        source = re.sub(r"```[^\n]*\n[\s\S]*?```", "", path.read_text())
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(repository.resolve()) or not resolved.exists():
                fail(path, "markdown_link", target)
            counts["authored_local_links"] += 1
        counts["authored_markdown"] += 1

    rea = repository / "evidence/rea-evidence.json.gz"
    try:
        with gzip.open(rea, "rt") as source:
            value = json.load(source)
        if not isinstance(value, (dict, list)):
            fail(rea, "rea_json", "expected object or array")
        counts["rea_gzip_json"] += 1
        del value
    except (OSError, ValueError) as exc:
        fail(rea, "rea_json", type(exc).__name__)

    for item in json.loads((repository / "manifests/claims.json").read_text())["claims"]:
        for source in item["sources"]:
            if not (repository / source).exists():
                fail(repository / "manifests/claims.json", "claim_source", f'{item["id"]}: {source}')
            counts["claim_source_links"] += 1

    zipped = repository / "evidence/unknown-content-probe-records.zip"
    try:
        with zipfile.ZipFile(zipped) as archive:
            expected_names = {str(path.relative_to(repository / "evidence"))
                              for path in (repository / "evidence/unknown-content-probe").rglob("*")
                              if path.is_file()}
            if set(archive.namelist()) != expected_names:
                fail(zipped, "zip_inventory", "archive file list differs from published experiment directory")
            for info in archive.infolist():
                path = repository / "evidence" / info.filename
                if not path.resolve().is_relative_to((repository / "evidence").resolve()):
                    fail(zipped, "zip_path", "member escapes evidence directory")
                    continue
                if path.is_file() and hashlib.sha256(archive.read(info)).hexdigest() != sha256(path):
                    fail(zipped, "zip_hash", info.filename)
                counts["zip_members"] += 1
    except (OSError, zipfile.BadZipFile) as exc:
        fail(zipped, "zip", type(exc).__name__)

    if not structural_only:
        inventory_path = repository / "manifests/published-files.json"
        inventory = json.loads(inventory_path.read_text())
        excluded = set(inventory["self_exclusions"])
        listed = {item["path"] for item in inventory["files"]}
        actual = {str(path.relative_to(repository)) for path in paths} - excluded
        if actual != listed:
            fail(inventory_path, "inventory", json.dumps({"unlisted": sorted(actual - listed),
                                                           "missing": sorted(listed - actual)}))
        for item in inventory["files"]:
            path = repository / item["path"]
            if not path.is_file():
                continue
            if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
                fail(path, "published_hash", "size or SHA-256 mismatch")
            counts["published_hashes"] += 1
        expected_sums = "".join(f'{item["sha256"]}  {item["path"]}\n' for item in inventory["files"])
        if (repository / "SHA256SUMS").read_text() != expected_sums:
            fail(repository / "SHA256SUMS", "sums", "text differs from published inventory")
        catalog = json.loads((repository / "manifests/source-catalog.json").read_text())
        for item in catalog["files"]:
            if "published_path" not in item:
                continue
            path = repository / item["published_path"]
            if not path.is_file() or sha256(path) != item.get("published_sha256"):
                fail(path, "source_catalog_published_hash", "missing or mismatched published file")
            counts["source_catalog_published_hashes"] += 1

    return {"status": "passed" if not errors else "failed", "offline_only": True,
            "structural_only": structural_only, "checks": dict(counts), "errors": errors,
            "scope": "all repository JSON/JSONL with declared concatenated stream and negative-fixture formats; Python syntax; authored docs and claim links; published hashes; REA gzip JSON; sanitized experiment ZIP",
            "excluded_checks": ["network links", "historical/vendor Markdown links", "execution of evidence code", "model or cloud calls", "original-source hash equality after declared redactions"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--structural-only", action="store_true")
    args = parser.parse_args()
    report = verify(args.repository.resolve(), args.structural_only)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
