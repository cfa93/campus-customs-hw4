"""Append-only audit trail of the chatbot's agent loop.

Every tool the agent calls, plus the start and end of each chat run, is recorded
in ``output/audit_trail.json`` with a timestamp, the tool name, short arguments,
a short result summary and (where relevant) a stop reason. Old entries are kept
between runs — the file is loaded, appended to, and written back.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"

ARGS_MAX = 200
RESULT_MAX = 300


class AuditEntry(BaseModel):
    timestamp: str
    tool_name: str
    args: str
    result: str
    stop_reason: str | None = None


class AuditTrail(BaseModel):
    entries: list[AuditEntry] = []


def append_audit_entry(tool_name: str, args: object, result: str, stop_reason: str | None = None) -> None:
    """Append one audit record, keeping all existing entries."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    trail = AuditTrail()
    if AUDIT_PATH.exists():
        try:
            trail = AuditTrail.model_validate_json(AUDIT_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            trail = AuditTrail()  # start fresh if the file is unreadable

    args_text = args if isinstance(args, str) else json.dumps(args, default=str)
    trail.entries.append(
        AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            tool_name=tool_name,
            args=args_text[:ARGS_MAX],
            result=str(result)[:RESULT_MAX],
            stop_reason=stop_reason,
        )
    )
    AUDIT_PATH.write_text(trail.model_dump_json(indent=2), encoding="utf-8")
