# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
import unittest
import test_review_edges as review_fixtures
NOW=review_fixtures.NOW
ROLE=review_fixtures.ROLE
from career_pipeline import core as c


class ActionScopeTests(unittest.TestCase):
    def prepared_intent(self):
        fixture=review_fixtures.ReviewEdgeTests();fixture.setUp()
        state=fixture.fully_approved_packet()
        state=c.transition(state,ROLE,{'type':'intend_apply','intent_id':'INTENT-1'},NOW)
        state=c.transition(state,ROLE,{'type':'verify','verification_id':'INTENT-CHECK','outcome':'active','source_type':'employer','url':state['roles'][0]['canonical_url'],'evidence':'Fictional official posting explicitly accepting matching requisition applications.','purpose':'intention'},NOW)
        return state

    def test_new_intent_does_not_reuse_submission_consent(self):
        state=self.prepared_intent();role=state['roles'][0]
        state=c.transition(state,ROLE,{'type':'approve','approval_id':'SUB-1','actor':'human','kind':'submission','fingerprint':c.submission_fingerprint(state,role),'note':'Fictional one-time action decision; no adapter exists'},NOW)
        role=state['roles'][0]
        self.assertTrue(c.approved(state,'submission',c.submission_fingerprint(state,role),ROLE))
        state=c.transition(state,ROLE,{'type':'intend_apply','intent_id':'INTENT-2'},'2026-11-02T14:01:00Z')
        self.assertFalse(c.approved(state,'submission',c.submission_fingerprint(state,state['roles'][0]),ROLE))
        self.assertFalse(c.verification_ready(state['roles'][0],'intention',c.stamp('2026-11-02T14:01:00Z')))

    def test_pre_submission_check_has_own_immediate_window(self):
        state=self.prepared_intent();role=state['roles'][0]
        self.assertFalse(c.verification_ready(role,'submission',c.stamp(NOW)))
        state=c.transition(state,ROLE,{'type':'verify','verification_id':'SUB-CHECK','outcome':'active','source_type':'employer','url':role['canonical_url'],'evidence':'Fictional execution-time official accepting-applications check.','purpose':'submission'},NOW)
        role=state['roles'][0]
        self.assertTrue(c.verification_ready(role,'submission',c.stamp('2026-11-02T14:04:59Z')))
        self.assertFalse(c.verification_ready(role,'submission',c.stamp('2026-11-02T14:06:00Z')))

    def test_changed_approved_claim_requires_new_fact_approval(self):
        state=self.prepared_intent();state['evidence']['claims'][0]['text']='Changed leadership claim awaiting candidate review.'
        self.assertFalse(c.packet_ready(state,state['roles'][0]))
        with self.assertRaises(c.PipelineError):c.transition(state,ROLE,{'type':'prepare_packet','sections':state['base_resume']['sections']},NOW)

    def test_inconclusive_http_success_is_not_observation(self):
        # A string in a note is not automated proof; the declared outcome must stay unknown.
        state=self.prepared_intent();role=state['roles'][0]
        state=c.transition(state,ROLE,{'type':'verify','verification_id':'BLOCKED','outcome':'unknown','source_type':'employer','url':role['canonical_url'],'evidence':'HTTP success but login blocks job content; cannot verify acceptance.','purpose':'intention'},'2026-11-02T14:01:00Z')
        self.assertEqual(state['roles'][0]['job_status'],'unknown')
        self.assertFalse(c.verification_ready(state['roles'][0],'intention',c.stamp('2026-11-02T14:01:00Z')))


if __name__=='__main__':unittest.main()
