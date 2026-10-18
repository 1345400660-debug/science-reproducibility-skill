"""Compare a delivery ZIP to its approved staging directory without extracting."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zipfile


def safe_name(name: str) -> bool:
    return bool(name) and "\\" not in name and ":" not in name and all(
        part not in ("", ".", "..") for part in name.split("/")
    )


def digest(stream) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def verify(source: Path, archive: Path, prefix: str, required: list[str]) -> list[str]:
    errors = []
    if not source.is_dir():
        return ["Source directory does not exist"]
    if prefix and not safe_name(prefix):
        return ["Unsafe archive prefix"]
    if not required or any(not safe_name(name) for name in required):
        return ["At least one safe required file path must be supplied"]
    files = {}
    for path in source.rglob("*"):
        if path.is_symlink():
            errors.append(f"Source symlink is not supported: {path.relative_to(source)}")
        elif path.is_file():
            files[path.relative_to(source).as_posix()] = path
    for name in required:
        if name not in files:
            errors.append(f"Required source file missing: {name}")
    archived = {}
    seen = set()
    head = prefix + "/" if prefix else ""
    try:
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                raw = info.filename.rstrip("/") if info.is_dir() else info.filename
                if not safe_name(raw):
                    errors.append(f"Unsafe archive path: {info.filename}")
                    continue
                if raw in seen:
                    errors.append(f"Duplicate archive path: {raw}")
                    continue
                seen.add(raw)
                if info.is_dir():
                    if prefix and raw != prefix and not raw.startswith(head):
                        errors.append(f"Unexpected archive directory: {raw}")
                    continue
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    errors.append(f"Archive symlink is not supported: {raw}")
                    continue
                if head and not raw.startswith(head):
                    errors.append(f"File outside archive prefix: {raw}")
                    continue
                name = raw[len(head):]
                with z.open(info) as stream:
                    archived[name] = digest(stream)
            for name in sorted(files.keys() - archived.keys()):
                errors.append(f"Archive file missing: {name}")
            for name in sorted(archived.keys() - files.keys()):
                errors.append(f"Unexpected archive file: {name}")
            for name in sorted(files.keys() & archived.keys()):
                with files[name].open("rb") as stream:
                    if digest(stream) != archived[name]:
                        errors.append(f"Content mismatch: {name}")
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, EOFError) as exc:
        errors.append(f"Cannot verify archive: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--required", action="append", required=True)
    args = parser.parse_args()
    errors = verify(args.source, args.archive, args.prefix, args.required)
    for error in errors:
        print("FAIL:", error)
    if not errors:
        print("PASS: required files and all archive bytes match the source directory.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
