"""Schema-backed ZIP intake: no extraction or executable input."""

import hashlib
from pathlib import Path
import stat
import unicodedata
import zipfile

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError

from .common import PhaseError, load_json_bytes, read_json

EXPECTED_MEMBERS = {"manifest.json", "SMART.en.md"}
MAX_MEMBER_BYTES = {"manifest.json": 64 * 1024, "SMART.en.md": 512 * 1024}
MAX_ZIP_BYTES = 640 * 1024


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def inspect_bundle(archive: Path, schema_path: Path) -> tuple[dict, bytes, str]:
    """Validate a bundle without extracting files or writing to disk."""
    try:
        if archive.stat().st_size > MAX_ZIP_BYTES:
            raise PhaseError("ZIP exceeds the intake size limit")
        with zipfile.ZipFile(archive) as zf:
            infos = zf.infolist()
            names = [x.filename for x in infos]
            if len(infos) != 2 or set(names) != EXPECTED_MEMBERS:
                raise PhaseError("ZIP must have exactly manifest.json and SMART.en.md")
            if len(set(unicodedata.normalize("NFC", x).casefold() for x in names)) != 2:
                raise PhaseError("ZIP contains duplicate/colliding member names")
            for info in infos:
                if info.flag_bits & 0x1:
                    raise PhaseError("Encrypted ZIP member not supported")
                if info.file_size > MAX_MEMBER_BYTES[info.filename]:
                    raise PhaseError("ZIP member exceeds size limit")
                if info.compress_size and info.file_size > max(1000, 100 * info.compress_size):
                    raise PhaseError("ZIP compression ratio exceeds limit")
                mode = info.external_attr >> 16
                if info.is_dir() or (info.create_system == 3 and stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                    raise PhaseError("ZIP contains a non-regular member")
            manifest_bytes = zf.read("manifest.json")
            english = zf.read("SMART.en.md")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise PhaseError("ZIP unavailable or malformed") from exc

    manifest = load_json_bytes(manifest_bytes)
    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(manifest)
    except (ValidationError, SchemaError) as exc:
        raise PhaseError("Manifest violates phase-start.schema.json: " + str(exc.message)[:180]) from exc
    if sha256(english) != manifest["documents"]["smart_english_sha256"]:
        raise PhaseError("English SMART SHA-256 does not match the manifest")
    try:
        english.decode("utf-8")
    except UnicodeError as exc:
        raise PhaseError("English SMART is not UTF-8") from exc
    return manifest, english, sha256(archive.read_bytes())
