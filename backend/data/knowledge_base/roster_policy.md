# Medics Online — Roster Policy

These rules govern how Dr. Eezy (and the roster generator) build a "balanced" work roster.

## General principles
1. **Fairness of workload**: Every staff member in the same job-title group should end
   up with as close to an equal number of shifts (and equal number of night/weekend
   shifts) as possible over the roster period.
2. **No back-to-back doubles without rest**: A staff member may not be scheduled for two
   consecutive shifts without at least one full rest period in between (e.g. no closing a
   night shift and opening the next day shift immediately after).
3. **Maximum consecutive night shifts**: No employee should be scheduled for more than
   3 consecutive night shifts.
4. **Job-title segregation**: Rosters are generated separately per job-title group
   (e.g. "Registered Nurse - ICU" staff are only used to cover ICU shifts; a Cardiologist
   is never used to fill a nursing shift, and vice versa). Doctors and nurses are
   rostered independently of each other.
5. **Minimum staffing per shift**: Each shift must be covered by at least the configured
   minimum number of staff for that job title (default: 1 for doctors on-call rotations,
   2 for ward/ICU nursing shifts, configurable per ward).
6. **Leave and unavailability**: Staff marked unavailable for a given date must never be
   assigned a shift on that date.

## Shift types
- **Day shift**: 07:00–19:00
- **Night shift**: 19:00–07:00
- **On-call**: available remotely, called in only if needed (used mostly for specialist doctors)

## Output
The generated roster should be exportable as a clean, printable PDF grouped by job title,
showing each staff member's name, their assigned shifts across the period, and total
shift count for a quick fairness check.
