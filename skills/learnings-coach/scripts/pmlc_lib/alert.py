"""The safety alert's grade (spec §6.2, P6-3, OD6-1). Task 1 holds the fixed copy the pack check needs; Task 2 adds
alert-grade (cmd_alert_grade, grade)."""
from __future__ import annotations

# Fixed copy (Phase 6, verbatim): where a pack's grade came from. "suggested" is the engine's own word for a grade it
# proposes and never appears in a pack: the skill asks the user, and the pack records "chosen by the user".
GRADE_SOURCES = ("register urgency", "chosen by the user")
