"""Rolling JSONL journal for crash-recovery (D-16).

Each tuning edit is appended as a single JSON line with fsync for crash safety.
One journal file per game session, capped at MAX_ENTRIES to prevent disk fill (T-28-07).
Journal directory is gitignored -- journals are ephemeral diagnostic data.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

JOURNAL_DIR = Path(__file__).resolve().parents[2] / "assets" / "journal"
MAX_ENTRIES = 10000  # Cap per session file (Pitfall 5, T-28-07)


class Journal:
    """Append-only JSONL journal writer for tuning edits."""

    def __init__(self):
        os.makedirs(JOURNAL_DIR, exist_ok=True)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = JOURNAL_DIR / f"session_{session_id}.jsonl"
        self._fd = open(self.path, "a", encoding="utf-8")
        self._count = 0

    def record(self, key, old_val, new_val, frame_count=0):
        """Append one edit entry. Flush + fsync for crash safety (T-28-06)."""
        if self._count >= MAX_ENTRIES:
            return  # Cap reached
        entry = {
            "t": time.time(),
            "f": frame_count,
            "k": key,
            "old": old_val,
            "new": new_val,
        }
        self._fd.write(json.dumps(entry, separators=(',', ':')) + "\n")
        self._fd.flush()
        os.fsync(self._fd.fileno())
        self._count += 1

    def close(self):
        """Close the journal file handle."""
        if self._fd and not self._fd.closed:
            self._fd.close()
