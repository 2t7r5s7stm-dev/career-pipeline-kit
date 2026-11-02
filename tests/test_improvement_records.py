# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""The improvement lifecycle is agent-operated; local records have bounded validation."""
import copy
import json
import unittest
from pathlib import Path
from career_pipeline import core

ROOT=Path(__file__).resolve().parents[1]
NOW='2026-11-02T12:00:00Z'


class ImprovementRecordTests(unittest.TestCase):
    def setUp(self):
        self.state=json.loads((ROOT/'examples/fictional/workspace.json').read_text())
        self.record=json.loads((ROOT/'examples/fictional/improvement-record.json').read_text())

    def with_record(self,record=None):
        self.state['improvements']=[copy.deepcopy(record or self.record)]
        return self.state

    def test_optional_record_preserves_earlier_state_compatibility(self):
        self.state.pop('improvements',None)
        self.assertEqual(core.validate(self.state,NOW),[])

    def test_retained_and_reverted_records_validate_and_preserve_history(self):
        state=self.with_record()
        self.assertEqual(core.validate(state,NOW),[])
        state['improvements'][0]['status']='reverted'
        state['improvements'][0]['decision']['rationale']='Fictional candidate preferred the earlier procedure; restore it in a new version.'
        self.assertEqual(core.validate(state,NOW),[])
        self.assertEqual(state['search_brief']['preferences'],json.loads((ROOT/'examples/fictional/workspace.json').read_text())['search_brief']['preferences'])

    def test_sensitive_proposal_can_wait_but_trial_needs_specific_approval(self):
        record=copy.deepcopy(self.record);record['affected_domains']=['filters'];record['status']='proposed'
        state=self.with_record(record)
        self.assertEqual(core.validate(state,NOW),[])
        state['improvements'][0]['status']='trial'
        self.assertTrue(any('specific recorded human approval' in e for e in core.validate(state,NOW)))
        state['improvements'][0]['approval']={'decision':'approved','by':'Fictional candidate','at':NOW,'note':'Fictional approval only for this bounded commute-filter trial and rollback.'}
        self.assertEqual(core.validate(state,NOW),[])

    def test_only_one_active_trial(self):
        state=self.with_record();state['improvements'][0]['status']='trial'
        second=copy.deepcopy(state['improvements'][0]);second['id']='IMP-EX-002';state['improvements'].append(second)
        self.assertTrue(any('one improvement trial' in e for e in core.validate(state,NOW)))

    def test_declared_safeguard_weakening_is_rejected(self):
        state=self.with_record();state['improvements'][0]['preserves_safeguards']=False
        self.assertTrue(core.validate(state,NOW))

    def test_trial_needs_baseline_boundary_stop_and_rollback(self):
        for field in ('baseline','measure','evaluation_boundary','stop_condition','rollback_checkpoint','rollback_action'):
            with self.subTest(field=field):
                state=copy.deepcopy(self.with_record());state['improvements'][0]['status']='trial';state['improvements'][0]['trial'][field]=''
                self.assertTrue(core.validate(state,NOW))

    def test_completed_review_needs_result_rationale_and_checkpoint(self):
        state=self.with_record();state['improvements'][0]['decision']['checkpoint']=''
        self.assertTrue(core.validate(state,NOW))
        state=self.with_record();state['improvements'][0]['trial']['result']=''
        self.assertTrue(core.validate(state,NOW))
        for field in ('by','rationale','checkpoint'):
            with self.subTest(field=field):
                state=self.with_record();state['improvements'][0]['decision'][field]='   '
                self.assertTrue(core.validate(state,NOW))

    def test_historical_versions_survive_later_profile_edits_without_decrement(self):
        state=self.with_record();state['search_brief']['version']=3
        self.assertEqual(core.validate(state,NOW),[])
        state['improvements'][0]['after_versions']['search_brief']=1
        state['improvements'][0]['before_versions']['search_brief']=2
        self.assertTrue(core.validate(state,NOW))

    def test_duplicate_improvement_ids_rejected(self):
        state=self.with_record();state['improvements'].append(copy.deepcopy(self.record))
        self.assertTrue(any('Improvement IDs' in e for e in core.validate(state,NOW)))


if __name__=='__main__':unittest.main()
