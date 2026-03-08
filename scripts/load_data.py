#!/usr/bin/env python3
"""
Load telemetry_logs.jsonl and employees.csv into the PostgreSQL database.
Uses bulk inserts for fast loading.

Usage (from project root):
    python scripts/load_data.py
"""

import csv
import json
import sys
import time
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.app.database import engine, create_db_and_tables
from backend.app.models.models import (
    Event, ApiRequest, ToolResult, ToolDecision, UserPrompt, ApiError, Employee
)

DATA_DIR = Path(__file__).parent.parent / "data"


def parse_event(message_json: dict) -> dict:
    """Parse a single nested log event message into flat dicts for our models."""
    attrs = message_json.get("attributes", {})
    resource = message_json.get("resource", {})
    event_name = attrs.get("event.name", "")

    # Common event fields
    base = {
        "event_timestamp": attrs.get("event.timestamp"),
        "event_type": event_name,
        "user_id": attrs.get("user.id"),
        "user_email": attrs.get("user.email", ""),
        "user_practice": resource.get("user.practice"),
        "session_id": attrs.get("session.id"),
        "organization_id": attrs.get("organization.id"),
        "os_type": resource.get("os.type"),
        "terminal_type": attrs.get("terminal.type"),
        "host_arch": resource.get("host.arch"),
    }

    detail = {}
    if event_name == "api_request":
        detail = {
            "model": attrs.get("model", ""),
            "input_tokens": int(attrs.get("input_tokens", 0)),
            "output_tokens": int(attrs.get("output_tokens", 0)),
            "cost_usd": float(attrs.get("cost_usd", 0)),
            "duration_ms": int(attrs.get("duration_ms", 0)),
            "cache_read_tokens": int(attrs.get("cache_read_tokens", 0)),
            "cache_creation_tokens": int(attrs.get("cache_creation_tokens", 0)),
        }
    elif event_name == "tool_result":
        detail = {
            "tool_name": attrs.get("tool_name", ""),
            "success": attrs.get("success", "false").lower() == "true",
            "duration_ms": int(attrs.get("duration_ms", 0)),
            "decision_type": attrs.get("decision_type", ""),
        }
    elif event_name == "tool_decision":
        detail = {
            "tool_name": attrs.get("tool_name", ""),
            "decision": attrs.get("decision", ""),
            "source": attrs.get("source", ""),
        }
    elif event_name == "user_prompt":
        detail = {
            "prompt_length": int(attrs.get("prompt_length", 0)),
        }
    elif event_name == "api_error":
        detail = {
            "error_message": attrs.get("error", ""),
            "status_code": attrs.get("status_code"),
            "model": attrs.get("model"),
            "attempt": int(attrs.get("attempt", 1)),
            "duration_ms": int(attrs.get("duration_ms", 0)),
        }

    return {"base": base, "type": event_name, "detail": detail}


def load_employees():
    """Load employees.csv using bulk insert."""
    csv_path = DATA_DIR / "employees.csv"
    if not csv_path.exists():
        print(f"⚠ {csv_path} not found, skipping employees.")
        return 0

    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM employees"))
        if rows:
            conn.execute(Employee.__table__.insert(), rows)

    print(f"✓ Loaded {len(rows)} employees")
    return len(rows)


def load_telemetry():
    """Load telemetry_logs.jsonl using bulk inserts."""
    jsonl_path = DATA_DIR / "telemetry_logs.jsonl"
    if not jsonl_path.exists():
        print(f"⚠ {jsonl_path} not found, skipping telemetry.")
        return 0

    # Phase 1: Parse all events into memory
    print("  Phase 1: Parsing JSONL file...")
    start = time.time()

    event_rows = []
    detail_map = {
        "api_request": [],
        "tool_result": [],
        "tool_decision": [],
        "user_prompt": [],
        "api_error": [],
    }

    with open(jsonl_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"⚠ Skipping line {line_num}: {e}")
                continue

            for log_event in record.get("logEvents", []):
                try:
                    message = json.loads(log_event.get("message", ""))
                except json.JSONDecodeError:
                    continue

                parsed = parse_event(message)
                event_rows.append(parsed["base"])
                if parsed["type"] in detail_map and parsed["detail"]:
                    detail_map[parsed["type"]].append(parsed["detail"])

    parse_time = time.time() - start
    print(f"  Parsed {len(event_rows)} events in {parse_time:.1f}s")

    # Phase 2: Bulk insert events, get assigned IDs
    print("  Phase 2: Bulk inserting events...")
    start = time.time()

    BATCH = 10000

    with engine.begin() as conn:
        # Insert events in batches, collecting IDs
        all_event_ids = []
        for i in range(0, len(event_rows), BATCH):
            batch = event_rows[i:i + BATCH]
            result = conn.execute(
                Event.__table__.insert().returning(Event.__table__.c.event_id),
                batch
            )
            ids = [row[0] for row in result]
            all_event_ids.extend(ids)
            print(f"    ... {min(i + BATCH, len(event_rows))}/{len(event_rows)} events inserted")

    insert_time = time.time() - start
    print(f"  Inserted {len(all_event_ids)} events in {insert_time:.1f}s")

    # Phase 3: Assign event_ids to detail rows and bulk insert them
    print("  Phase 3: Inserting detail tables...")
    start = time.time()

    # Build index: map each sequential event to its event_id
    detail_idx = {
        "api_request": 0,
        "tool_result": 0,
        "tool_decision": 0,
        "user_prompt": 0,
        "api_error": 0,
    }

    for idx, row in enumerate(event_rows):
        etype = row["event_type"]
        if etype in detail_idx and detail_idx[etype] < len(detail_map[etype]):
            detail_map[etype][detail_idx[etype]]["event_id"] = all_event_ids[idx]
            detail_idx[etype] += 1

    table_map = {
        "api_request": ApiRequest,
        "tool_result": ToolResult,
        "tool_decision": ToolDecision,
        "user_prompt": UserPrompt,
        "api_error": ApiError,
    }

    with engine.begin() as conn:
        for etype, model_cls in table_map.items():
            rows = detail_map[etype]
            if not rows:
                continue
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                conn.execute(model_cls.__table__.insert(), batch)
            print(f"    ✓ {etype}: {len(rows)} rows")

    detail_time = time.time() - start
    print(f"  Detail tables inserted in {detail_time:.1f}s")
    print(f"✓ Loaded {len(event_rows)} telemetry events (total: {parse_time + insert_time + detail_time:.1f}s)")
    return len(event_rows)


def main():
    print("Creating tables (if not exist)...")
    create_db_and_tables()

    print("\nLoading data into database...")
    load_employees()
    load_telemetry()

    print("\n✓ Data loading complete!")


if __name__ == "__main__":
    main()
