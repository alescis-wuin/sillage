"""Local, out-of-repository recovery evidence for partially completed phase starts."""

import json
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import tempfile

from .common import PhaseError, read_json


def journal_path(root: Path, state_directory: Path, manifest: dict) -> Path:
    state_directory = state_directory.expanduser().resolve()
    if state_directory == root.resolve() or root.resolve() in state_directory.parents:
        raise PhaseError("Recovery journal must be outside the Git repository")
    repository = manifest["git"]["github_repository"].lower().replace("/", "-")
    return state_directory / f"{repository}-{manifest['phase'].lower()}.json"


def read_existing(path: Path, *, resume: bool, digest: str, root: Path) -> dict | None:
    if not path.exists():
        if resume:
            raise PhaseError("Cannot resume: no previous journal exists")
        return None
    if not resume:
        raise PhaseError("A phase journal already exists; explicit --resume is required")
    record = read_json(path)
    if record.get("bundle_sha256") != digest or record.get("repository_root") != str(root.resolve()):
        raise PhaseError("Recovery journal does not match the current bundle and repository")
    return record


def save(path: Path, record: dict, *, first: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if first:
        try:
            with path.open("x", encoding="utf-8") as out:
                json.dump(record, out, indent=2, sort_keys=True)
                out.write("\n")
            path.chmod(0o600)
        except FileExistsError as exc:
            raise PhaseError("Concurrent phase journal exists; review before retry") from exc
        return
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.chmod(temporary, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(record, out, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def exclusive_apply_lock(path: Path):
    """Prevent concurrent owner apply/resume instances on the proposed Linux host."""
    lock_path = path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        with os.fdopen(fd, "w") as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
    except BlockingIOError as exc:
        raise PhaseError("Another phase-start apply is already running") from exc
