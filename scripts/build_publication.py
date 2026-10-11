#!/usr/bin/env python3
"""Build a path-redacted research mirror; never read authentication stores."""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sanitize(text: str, source: Path) -> tuple[str, dict[str, int]]:
    counts: Counter[str] = Counter()
    researcher_home = str(Path.home())
    replacements = [
        (str(source), "/research/claude-workflow-research", "research-root"),
        (re.sub(r"[^a-zA-Z0-9]", "-", str(source)), "research-workspace", "normalized-encoded-root"),
        (str(source).replace("/", "-"), "research-workspace", "encoded-root"),
        (researcher_home, "/home/researcher", "home-path"),
        (researcher_home.replace("/", "-"), "-home-researcher", "encoded-home"),
    ]
    for old, new, rule in replacements:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            counts[rule] += n
    for pattern, replacement, rule in [
        (r"/(?:private/)?var/folders/[^/\s\"']+/[^/\s\"']+/", "/tmp/host-temporary/", "mac-temp-root"),
        (r"/(?:private/)?tmp/claude-\d+/", "/tmp/claude-user/", "temp-user-id"),
    ]:
        text, n = re.subn(pattern, replacement, text)
        counts[rule] += n
    pattern = re.compile(r'(\"(?:userEmail|organizationUuid|accountUuid|workspace_id)\"\s*:\s*\")([^\"]+)(\")')

    def redact_identity(match: re.Match[str]) -> str:
        counts["account-metadata"] += 1
        label = "identity-" + digest(match.group(2).encode())[:12]
        return match.group(1) + label + match.group(3)

    text = pattern.sub(redact_identity, text)
    return text, {k: v for k, v in counts.items() if v}


def classify(relative: Path, symlink: bool) -> tuple[str, str]:
    parts = relative.parts
    name = str(relative)
    if symlink:
        return "omitted", "symlink; underlying regular files are archived separately"
    if ".git" in parts or "__pycache__" in parts or relative.suffix == ".pyc" or relative.name == ".DS_Store":
        return "omitted", "VCS/cache/OS byproduct; not experimental evidence"
    if name in {"native-latest/package/claude", "native-latest.tgz", "tools/ant-1.40.0/ant", "tools/ant-1.40.0/download.zip"}:
        return "release-or-upstream", "large official distribution; retrieve using manifest or private release asset"
    if name == "unknown-content-probe-records.zip":
        return "rebuilt", "archive rebuilt from the published redacted experiment records"
    return "copy", ""


def rebuild_experiment_zip(repository: Path) -> None:
    evidence = repository / "evidence"
    source = evidence / "unknown-content-probe"
    if not source.exists():
        return
    with zipfile.ZipFile(evidence / "unknown-content-probe-records.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, str(path.relative_to(evidence)))


def refresh(repository: Path) -> None:
    rebuild_experiment_zip(repository)
    catalog_path = repository / "manifests/source-catalog.json"
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text())
        for item in catalog["files"]:
            target = repository / item.get("published_path", "__not_published__")
            if target.is_file():
                data = target.read_bytes()
                item["published_bytes"] = len(data)
                item["published_sha256"] = digest(data)
                item["byte_identical_to_source"] = item["source_sha256"] == digest(data)
        write_json(catalog_path, catalog)
    exclusions = {"manifests/published-files.json", "SHA256SUMS"}
    entries = []
    for path in sorted(repository.rglob("*")):
        rel = path.relative_to(repository)
        if not path.is_file() or ".git" in rel.parts or "__pycache__" in rel.parts or str(rel) in exclusions:
            continue
        data = path.read_bytes()
        entries.append({"path": str(rel), "bytes": len(data), "sha256": digest(data)})
    write_json(repository / "manifests/published-files.json", {
        "algorithm": "sha256", "self_exclusions": sorted(exclusions), "file_count": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries), "files": entries,
    })
    (repository / "SHA256SUMS").write_text("".join(f'{item["sha256"]}  {item["path"]}\n' for item in entries))
    print(json.dumps({"publishedFiles": len(entries), "publishedBytes": sum(item["bytes"] for item in entries)}))


def build(source: Path, repository: Path) -> None:
    source = source.resolve()
    repository = repository.resolve()
    if source == repository or source in repository.parents:
        raise SystemExit("destination must not be inside the source evidence directory")
    evidence = repository / "evidence"
    if evidence.exists():
        raise SystemExit("evidence mirror already exists; use --refresh after deliberate changes")
    evidence.mkdir(parents=True)
    entries = []
    redactions = []
    decisions: Counter[str] = Counter()
    for path in sorted(source.rglob("*")):
        if not path.is_file() and not path.is_symlink():
            continue
        rel = path.relative_to(source)
        action, reason = classify(rel, path.is_symlink())
        decisions[action] += 1
        if path.is_symlink():
            entries.append({"source_path": str(rel), "action": action, "reason": reason})
            continue
        original = path.read_bytes()
        entry = {"source_path": str(rel), "source_bytes": len(original), "source_sha256": digest(original), "action": action}
        if reason:
            entry["reason"] = reason
        if action in {"copy", "rebuilt"}:
            target = evidence / rel
            entry["published_path"] = str(target.relative_to(repository))
            if action == "copy":
                target.parent.mkdir(parents=True, exist_ok=True)
                payload = original
                rules: dict[str, int] = {}
                if str(rel) == "rea-evidence.json.gz":
                    decoded = gzip.decompress(original)
                    text, rules = sanitize(decoded.decode("utf-8"), source)
                    payload = gzip.compress(text.encode(), compresslevel=9, mtime=0) if rules else original
                else:
                    try:
                        text, rules = sanitize(original.decode("utf-8"), source)
                        payload = text.encode()
                    except UnicodeDecodeError:
                        pass
                target.write_bytes(payload)
                if rules:
                    redactions.append({"path": str(target.relative_to(repository)), "rules": rules})
        entries.append(entry)
    write_json(repository / "manifests/source-catalog.json", {
        "source_label": "original local claude-workflow-research evidence collection",
        "source_path_published": False, "decisions": dict(decisions), "files": entries,
    })
    write_json(repository / "manifests/redactions.json", {
        "policy": "redact researcher host paths and account identity metadata; retain task/agent/run IDs and causal timestamps",
        "raw_originals_modified": False, "redacted_files": len(redactions), "files": redactions,
    })
    refresh(repository)
    print(json.dumps({"sourceDecisions": dict(decisions), "redactedFiles": len(redactions)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--destination", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        refresh(args.destination)
    elif args.source:
        build(args.source, args.destination)
    else:
        parser.error("--source is required for initial publication")


if __name__ == "__main__":
    main()
