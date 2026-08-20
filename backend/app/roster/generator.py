"""
Balanced work roster generator.

Implements the rules in data/knowledge_base/roster_policy.md:
  - job-title segregation (each group is scheduled completely independently)
  - fairness (least-loaded staff picked first, balancing total shift counts)
  - no more than 3 consecutive night shifts
  - a rest period after a night shift (no immediate day shift the next day)
  - unavailable staff are never scheduled
  - configurable minimum staff per shift

This is a deterministic greedy scheduler — simple and transparent enough to explain
live in a demo, and to unit-test precisely. It's not a full constraint-solver, but it
satisfies all the stated policy rules for realistic small-team hospital rosters.
"""
from datetime import date, timedelta
from typing import Dict, List

# Per job-title shift configuration. Anything not listed falls back to DEFAULT_CONFIG.
JOB_TITLE_SHIFT_CONFIG = {
    "Registered Nurse - ICU": {"shifts": ["Day", "Night"], "min_staff": 1},
    "Registered Nurse - Pediatric Ward": {"shifts": ["Day", "Night"], "min_staff": 1},
    "Midwife": {"shifts": ["Day", "Night"], "min_staff": 1},
    "Theatre Nurse (Scrub Nurse)": {"shifts": ["Day"], "min_staff": 1},
    "Nurse Practitioner": {"shifts": ["Day"], "min_staff": 1},
    "General Practitioner": {"shifts": ["Day"], "min_staff": 1},
    "Cardiologist": {"shifts": ["Day"], "min_staff": 1},
    "Pediatrician": {"shifts": ["Day"], "min_staff": 1},
    "Orthopedic Surgeon": {"shifts": ["Day"], "min_staff": 1},
    "Anesthesiologist": {"shifts": ["Day"], "min_staff": 1},
}
DEFAULT_CONFIG = {"shifts": ["Day"], "min_staff": 1}
MAX_CONSECUTIVE_NIGHTS = 3


def _config_for(job_title: str) -> dict:
    return JOB_TITLE_SHIFT_CONFIG.get(job_title, DEFAULT_CONFIG)


def generate_roster(staff: List[dict], start_date: date, num_days: int = 7) -> dict:
    """
    Returns:
        {
          "<job_title>": {
              "dates": [{"date": "YYYY-MM-DD", "shifts": {"Day": [names], "Night": [names]}}, ...],
              "totals": {"<staff name>": <shift count>},
              "warnings": ["..."]
          },
          ...
        }
    """
    by_title: Dict[str, list] = {}
    for member in staff:
        by_title.setdefault(member["job_title"], []).append(member)

    roster = {}
    for job_title, employees in by_title.items():
        roster[job_title] = _generate_for_group(job_title, employees, start_date, num_days)
    return roster


def _generate_for_group(job_title: str, employees: List[dict], start_date: date, num_days: int) -> dict:
    config = _config_for(job_title)
    shift_types = config["shifts"]
    min_staff = config["min_staff"]

    counts = {e["id"]: 0 for e in employees}
    night_streak = {e["id"]: 0 for e in employees}
    last_shift_type = {e["id"]: None for e in employees}
    warnings = []
    date_entries = []

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.isoformat()
        assigned_today_ids = set()
        shifts_today = {}

        for shift in shift_types:
            eligible = [
                e for e in employees
                if date_str not in e.get("unavailable_dates", [])
                and e["id"] not in assigned_today_ids
            ]
            if shift == "Night":
                eligible = [e for e in eligible if night_streak[e["id"]] < MAX_CONSECUTIVE_NIGHTS]
            else:
                # Rest rule: no day shift the day right after a night shift.
                eligible = [e for e in eligible if last_shift_type[e["id"]] != "Night"]

            # Fairness: least-loaded staff first.
            eligible.sort(key=lambda e: counts[e["id"]])
            chosen = eligible[:min_staff]

            if len(chosen) < min_staff:
                warnings.append(
                    f"{job_title}: understaffed on {date_str} ({shift}) — "
                    f"needed {min_staff}, found {len(chosen)} eligible."
                )

            shifts_today[shift] = [c["name"] for c in chosen]
            for c in chosen:
                assigned_today_ids.add(c["id"])
                counts[c["id"]] += 1

        # Update per-employee streaks/rest tracking for the next iteration.
        for e in employees:
            assigned_shift = next((s for s in shift_types if e["name"] in shifts_today[s]), None)
            last_shift_type[e["id"]] = assigned_shift
            night_streak[e["id"]] = night_streak[e["id"]] + 1 if assigned_shift == "Night" else 0

        date_entries.append({"date": date_str, "shifts": shifts_today})

    totals = {e["name"]: counts[e["id"]] for e in employees}
    return {"dates": date_entries, "totals": totals, "warnings": warnings}
