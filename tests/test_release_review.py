# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Focused release regressions for ambiguous human-reported application history."""
import json
import unittest
from pathlib import Path

from career_pipeline import core

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-11-02T12:00:00Z"
ROLE_ID = "role-001"


class ReleaseReviewTests(unittest.TestCase):
    def ambiguous_then_clerical_reset(self):
        state = json.loads((ROOT / "validation/fictional-walkthrough/workspace/workspace.json").read_text())
        state = core.transition(state, ROLE_ID, {
            "type": "record_application", "actor": "human", "status": "submitted_unconfirmed",
            "external_reference": "Fictional timeout after a manual attempt; no receipt yet.",
        }, NOW)
        return core.transition(state, ROLE_ID, {
            "type": "record_application", "actor": "human", "status": "not_applied",
            "external_reference": "Fictional clerical status reset; history has not been reconciled.",
        }, NOW)

    def test_ambiguous_history_still_requires_review_after_status_reset(self):
        state = self.ambiguous_then_clerical_reset()
        action = next(a["action"] for a in core.next_actions(state, NOW) if a["role_id"] == ROLE_ID)
        self.assertIn("application history", action.lower())
        self.assertNotIn("Ready for manual application", action)
        self.assertTrue(any("history" in reason.lower() for reason in core.submission_gate(state, state["roles"][0], NOW)))

    def test_ambiguous_history_suppresses_reminder_after_status_reset(self):
        state = self.ambiguous_then_clerical_reset()
        self.assertTrue(state["reminder_preferences"]["opted_in"])
        self.assertTrue(state["reminders"][0]["enabled"])
        self.assertEqual([], core.due_reminders(state, NOW))
        self.assertEqual(2, len(state["roles"][0]["application"]["history"]))


if __name__ == "__main__":
    unittest.main()
