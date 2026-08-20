"""
Checkpoint tests for the roster generator + PDF export.

Verifies the policy rules from data/knowledge_base/roster_policy.md are actually
enforced: job-title segregation, unavailability, max 3 consecutive nights, rest
after a night shift, and reasonably balanced (fair) shift totals — then confirms
a real PDF file is produced.
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.roster.generator import generate_roster
from app.roster.pdf_export import export_roster_to_pdf

STAFF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "staff.json")


def load_staff():
    with open(STAFF_PATH) as f:
        return json.load(f)


def test_job_title_segregation():
    staff = load_staff()
    roster = generate_roster(staff, start_date=date(2026, 8, 20), num_days=7)

    # Doctors and nurses must never appear in the same job-title group.
    doctor_titles = {s["job_title"] for s in staff if s["profession"] == "Doctor"}
    nurse_titles = {s["job_title"] for s in staff if s["profession"] == "Nurse"}
    assert doctor_titles.isdisjoint(nurse_titles)
    assert set(roster.keys()) == doctor_titles | nurse_titles


def test_unavailability_is_respected():
    staff = load_staff()
    roster = generate_roster(staff, start_date=date(2026, 8, 20), num_days=7)

    icu = roster["Registered Nurse - ICU"]
    for entry in icu["dates"]:
        if entry["date"] == "2026-08-20":
            all_assigned = sum(entry["shifts"].values(), [])
            assert "James Botha" not in all_assigned, "James Botha marked unavailable on 2026-08-20"


def test_max_three_consecutive_nights_and_rest_rule():
    staff = load_staff()
    roster = generate_roster(staff, start_date=date(2026, 8, 20), num_days=14)
    icu = roster["Registered Nurse - ICU"]
    all_names = [s["name"] for s in staff if s["job_title"] == "Registered Nurse - ICU"]

    streak = {name: 0 for name in all_names}
    # prev_shift must be tracked for EVERY employee on EVERY calendar day (including
    # days they aren't scheduled at all, which resets it to None) so that "immediately
    # after" always means the very next calendar day, not the next day they happen
    # to work.
    prev_shift = {name: None for name in all_names}
    for entry in icu["dates"]:
        night_names = set(entry["shifts"].get("Night", []))
        day_names = set(entry["shifts"].get("Day", []))
        for name in all_names:
            if prev_shift[name] == "Night" and name in day_names:
                raise AssertionError(f"{name} was given a Day shift immediately after a Night shift")
            was_night = name in night_names
            streak[name] = streak[name] + 1 if was_night else 0
            assert streak[name] <= 3, f"{name} exceeded 3 consecutive night shifts"
            prev_shift[name] = "Night" if was_night else ("Day" if name in day_names else None)


def test_shift_totals_are_reasonably_balanced():
    staff = load_staff()
    roster = generate_roster(staff, start_date=date(2026, 8, 20), num_days=14)
    icu_totals = list(roster["Registered Nurse - ICU"]["totals"].values())
    # With 3 ICU nurses covering 14 days x 2 shifts fairly, no one should be
    # worked drastically more than the others.
    assert max(icu_totals) - min(icu_totals) <= 3


def test_pdf_export_produces_a_real_file(tmp_path):
    staff = load_staff()
    roster = generate_roster(staff, start_date=date(2026, 8, 20), num_days=7)
    out_path = str(tmp_path / "roster.pdf")
    export_roster_to_pdf(roster, out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 1000  # a real multi-page PDF, not an empty stub
    with open(out_path, "rb") as f:
        assert f.read(4) == b"%PDF"
