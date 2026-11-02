# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Independent review fixtures. Every candidate and employer is fictional."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from career_pipeline import core as c


ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-11-02T14:00:00Z"
ROLE = "role-001"


class ReviewEdgeTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((ROOT / "examples/fictional/workspace.json").read_text())

    def prepare(self):
        state = c.transition(self.state, ROLE, {
            "type": "approve", "kind": "facts", "actor": "human",
            "note": "Fictional candidate reviewed the supplied evidence.",
            "fingerprint": c.facts_fingerprint(self.state), "approval_id": "TEST-FACTS",
        }, NOW)
        return c.transition(state, ROLE, {
            "type": "prepare_packet", "sections": state["base_resume"]["sections"],
        }, NOW)

    def fully_approved_packet(self):
        state = self.prepare()
        role = c.get_role(state, ROLE)
        state = c.transition(state, ROLE, {
            "type": "approve", "kind": "role_selection", "actor": "human",
            "note": "Fictional candidate selects this fictional role for review.",
            "fingerprint": c.role_fingerprint(state, role), "approval_id": "TEST-ROLE",
        }, NOW)
        role = c.get_role(state, ROLE)
        state = c.transition(state, ROLE, {
            "type": "qa_pass", "fingerprint": role["packet"]["fingerprint"],
            "reviewer": "Independent fictional reviewer",
            "checks": ["Confirmed selected evidence IDs, attribution and readable Markdown."],
        }, NOW)
        role = c.get_role(state, ROLE)
        return c.transition(state, ROLE, {
            "type": "approve", "kind": "materials", "actor": "human",
            "note": "Fictional candidate approves the exact local draft.",
            "fingerprint": role["packet"]["fingerprint"], "approval_id": "TEST-MATERIALS",
        }, NOW)

    def intent_verified(self):
        state = c.transition(self.state, ROLE, {"type": "intend_apply", "intent_id": "TEST-INTENT"},
                             "2026-11-02T12:00:00Z")
        return c.transition(state, ROLE, {
            "type": "verify", "verification_id": "TEST-VERIFY", "outcome": "active",
            "source_type": "employer", "url": state["roles"][0]["canonical_url"],
            "evidence": "Fictional official snapshot states that this requisition accepts applications.",
            "purpose": "intention",
        }, "2026-11-02T12:05:00Z")

    def test_example_validates(self):
        self.assertEqual([], c.validate(self.state, NOW))

    def test_unapproved_facts_cannot_produce_packet(self):
        with self.assertRaises(c.PipelineError):
            c.transition(self.state, ROLE, {"type": "prepare_packet", "sections": []}, NOW)

    def test_unresolved_metrics_stay_out_of_resume(self):
        state = self.prepare()
        self.assertNotIn("40%", c.render_packet(state, ROLE, NOW)["resume.md"])
        with self.assertRaises(c.PipelineError):
            c.transition(state, ROLE, {"type": "prepare_packet", "sections": [
                {"heading": "Experience", "evidence_ids": ["E-004"]},
            ]}, NOW)

    def test_numeric_substring_is_not_metric_confirmation(self):
        claim = self.state["evidence"]["claims"][0]
        claim["text"] = "Improved quality 50% with 5 peers."
        claim["metrics"] = [{
            "value": "50%", "unit": "percent", "baseline": "fictional baseline",
            "period": "fictional period", "attribution": "team", "source": "fictional source",
            "confirmed": True,
        }]
        self.assertTrue(c.validate(self.state, NOW), "The unsupported numeric 5 needs separate confirmation.")

    def test_packet_readiness_never_records_application(self):
        state = self.fully_approved_packet()
        role = c.get_role(state, ROLE)
        self.assertTrue(c.packet_ready(state, role))
        self.assertEqual("not_applied", role["application"]["status"])
        self.assertEqual([], role["application"]["history"])

    def test_stale_packet_can_be_reprepared_and_preserved(self):
        state = self.prepare()
        old_fingerprint = state["roles"][0]["packet"]["fingerprint"]
        state["style_guide"]["version"] += 1
        self.assertEqual([], c.validate(state, NOW))
        self.assertFalse(c.packet_ready(state, state["roles"][0]))
        with self.assertRaises(c.PipelineError):
            c.render_packet(state, ROLE, NOW)
        refreshed = c.transition(state, ROLE, {
            "type": "prepare_packet", "sections": state["base_resume"]["sections"],
        }, NOW)
        self.assertEqual(2, refreshed["roles"][0]["packet"]["version"])
        self.assertEqual(old_fingerprint, refreshed["roles"][0]["packet_history"][0]["fingerprint"])

    def test_material_role_change_invalidates_exact_approval_even_without_version_bump(self):
        state = self.fully_approved_packet()
        role = c.get_role(state, ROLE)
        original = c.role_fingerprint(state, role)
        role["work_arrangement"] = "Requires daily attendance in a different fictional region"
        self.assertNotEqual(original, c.role_fingerprint(state, role))
        self.assertFalse(c.packet_ready(state, role))

    def test_bad_timestamp_is_validation_error_not_exception(self):
        state = self.intent_verified()
        state["roles"][0]["verifications"][0]["at"] = "not-a-date"
        self.assertTrue(c.validate(state, NOW))

    def test_current_official_observation_can_support_intention(self):
        role = self.intent_verified()["roles"][0]
        self.assertTrue(c.verification_ready(role, "intention", c.stamp(NOW)))
        self.assertFalse(c.verification_ready(role, "intention", c.stamp("2026-11-04T14:00:00Z")))

    def test_posting_age_is_not_action_verification_age(self):
        state = self.intent_verified()
        role = state["roles"][0]
        role["posting_date"] = "2025-01-01"
        self.assertTrue(c.verification_ready(role, "intention", c.stamp(NOW)))

    def test_latest_unknown_does_not_reuse_earlier_active(self):
        state = self.intent_verified()
        state = c.transition(state, ROLE, {
            "type": "verify", "verification_id": "TEST-BLOCKED", "outcome": "unknown",
            "source_type": "other", "url": state["roles"][0]["canonical_url"],
            "evidence": "Login blocked; accepting-applications status could not be observed.",
            "purpose": "intention",
        }, "2026-11-02T13:00:00Z")
        role = state["roles"][0]
        self.assertEqual("unknown", role["job_status"])
        self.assertFalse(c.verification_ready(role, "intention", c.stamp(NOW)))

    def test_aggregator_cannot_confirm_active(self):
        with self.assertRaises(c.PipelineError):
            c.transition(self.state, ROLE, {
                "type": "verify", "verification_id": "TEST-AGG", "outcome": "active",
                "source_type": "aggregator", "url": "https://leads.example.invalid/job",
                "evidence": "Aggregator says active.", "purpose": "discovery",
            }, NOW)

    def test_closed_after_tailoring_keeps_packet_but_stops_apply_action(self):
        state = self.prepare()
        fingerprint = state["roles"][0]["packet"]["fingerprint"]
        state = c.transition(state, ROLE, {
            "type": "verify", "verification_id": "TEST-CLOSED", "outcome": "closed",
            "source_type": "employer", "url": state["roles"][0]["canonical_url"],
            "evidence": "Fictional official posting says applications are closed.", "purpose": "discovery",
        }, NOW)
        self.assertEqual(fingerprint, state["roles"][0]["packet"]["fingerprint"])
        action = next(a["action"] for a in c.next_actions(state, NOW) if a["role_id"] == ROLE)
        self.assertIn("closed", action)
        self.assertEqual([], c.due_reminders(state, NOW))

    def test_new_requisition_has_distinct_history(self):
        role = copy.deepcopy(self.state["roles"][0])
        role.update(id="role-002", requisition_id="EX-102",
                    canonical_url="https://careers.example.invalid/jobs/EX-102", related_role_ids=[ROLE])
        role["identity_key"] = c.identity(role)
        self.state["roles"].append(role)
        self.assertEqual([], c.validate(self.state, NOW))
        self.assertNotEqual(self.state["roles"][0]["identity_key"], role["identity_key"])
        self.assertEqual([], role["application"]["history"])

    def test_reminder_cycle_is_persistently_deduplicated(self):
        due = c.due_reminders(self.state, NOW)[0]
        state = c.acknowledge_reminder(self.state, due["id"], due["dedupe_key"], NOW)
        reloaded = json.loads(json.dumps(state))
        self.assertEqual([], c.due_reminders(reloaded, NOW))
        with self.assertRaises(c.PipelineError):
            c.acknowledge_reminder(reloaded, due["id"], due["dedupe_key"], NOW)

    def test_reminder_opt_out_snooze_and_stop(self):
        self.state["reminder_preferences"]["opted_in"] = False
        self.assertEqual([], c.due_reminders(self.state, NOW))
        self.state["reminder_preferences"]["opted_in"] = True
        snoozed = c.transition(self.state, ROLE, {
            "type": "snooze_reminder", "reminder_id": "REM-001", "until": "2026-11-03T14:00:00Z",
        }, NOW)
        self.assertEqual([], c.due_reminders(snoozed, NOW))
        stopped = c.transition(self.state, ROLE, {"type": "stop_reminder", "reminder_id": "REM-001"}, NOW)
        self.assertEqual([], c.due_reminders(stopped, NOW))

    def test_absent_adapter_blocks_even_approved_materials(self):
        state = self.fully_approved_packet()
        state["adapter_capabilities"]["submission"] = True
        reasons = c.submission_gate(state, state["roles"][0], NOW)
        self.assertTrue(any("No submission adapter" in reason for reason in reasons))

    def test_packet_dry_run_has_no_filesystem_or_state_effect(self):
        state = self.prepare()
        before = copy.deepcopy(state)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "new-packet"
            manifest = c.write_packet(state, ROLE, out, NOW, dry_run=True)
            self.assertFalse(out.exists())
            self.assertEqual(1, manifest["packet_version"])
        self.assertEqual(before, state)


if __name__ == "__main__":
    unittest.main()
