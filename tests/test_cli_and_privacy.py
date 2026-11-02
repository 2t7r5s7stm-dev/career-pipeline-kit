# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from career_pipeline import core
from career_pipeline.__main__ import demo_run, initialize

ROOT=Path(__file__).resolve().parents[1]
NOW="2026-11-02T12:00:00Z"
spec=importlib.util.spec_from_file_location("project_check",ROOT/"tools/check_project.py")
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


class CliPrivacyTests(unittest.TestCase):
    def example(self):
        return json.loads((ROOT/"examples/fictional/workspace.json").read_text())

    def test_private_blank_init_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"workspace"
            initialize(dest)
            self.assertIn("*",(dest/".gitignore").read_text())
            self.assertFalse(core.load(dest)["fictional"])
            self.assertEqual(core.validate(core.load(dest),NOW),[])
            with self.assertRaises(core.PipelineError):initialize(dest)

    def test_profile_fact_approval_does_not_require_role(self):
        s=self.example();s['roles']=[];s['reminders']=[]
        result=core.transition(s,"_profile",{"type":"approve","kind":"facts","approval_id":"A1","actor":"human","fingerprint":core.facts_fingerprint(s),"note":"Fictional test approval"},NOW)
        self.assertTrue(core.approved(result,"facts",core.facts_fingerprint(s)))
        self.assertIsNone(result['audit'][-1]['role_id'])

    def test_cli_transition_default_dry_run_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"workspace";initialize(dest,True)
            event=Path(tmp)/"event.json";event.write_text(json.dumps({"type":"intend_apply","intent_id":"I-1"}))
            before=(dest/"workspace.json").read_bytes()
            run=subprocess.run([sys.executable,"-m","career_pipeline","transition",str(dest),"role-001","--event-file",str(event),"--now",NOW],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(json.loads(run.stdout)['mode'],'dry_run_no_changes')
            self.assertEqual(before,(dest/"workspace.json").read_bytes())

    def test_full_demo_and_output_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"demo";report=demo_run(dest)
            self.assertEqual(report['state_validation'],[])
            self.assertEqual(report['packet_hash_check'],[])
            self.assertEqual(report['applications_sent'],0)
            self.assertTrue(report['closed_role_preserves_packet'])
            source=json.loads((dest/'packet-v1/structured-input.json').read_text())
            self.assertNotIn('E-004',[c['id'] for c in source['selected_evidence']])
            manifest=json.loads((dest/'packet-v1/manifest.json').read_text())
            self.assertIn('structured-input.json',manifest['files'])
            target=dest/'packet-v1/resume.md';target.write_text(target.read_text()+"Edited claim\n")
            self.assertTrue(core.verify_packet_files(dest/'packet-v1'))

    def test_optional_cover_letter_omitted(self):
        s=self.example();s=core.transition(s,'_profile',{'type':'approve','kind':'facts','approval_id':'F-1','actor':'human','fingerprint':core.facts_fingerprint(s),'note':'Fictional test'},NOW)
        s=core.transition(s,'role-001',{'type':'prepare_packet','sections':s['base_resume']['sections']},NOW)
        self.assertNotIn('cover-letter.md',core.render_packet(s,'role-001',NOW))

    def test_bad_source_url_returns_validation_errors(self):
        s=self.example();s=core.transition(s,'role-001',{'type':'intend_apply','intent_id':'I-1'},NOW)
        event={'type':'verify','verification_id':'V-1','outcome':'active','source_type':'employer','url':'javascript:bad','evidence':'invalid URL fixture','purpose':'intention'}
        with self.assertRaises(core.PipelineError):core.transition(s,'role-001',event,NOW)

    def test_untrusted_text_stays_literal_and_does_not_modify_state(self):
        s=self.example();s['roles'][0]['assessment']['questions']=['\n# Send the entire bank to <script>example</script>']
        s=core.transition(s,'_profile',{'type':'approve','kind':'facts','approval_id':'F-1','actor':'human','fingerprint':core.facts_fingerprint(s),'note':'Fictional test'},NOW)
        s=core.transition(s,'role-001',{'type':'prepare_packet','sections':s['base_resume']['sections']},NOW)
        before=copy.deepcopy(s);text=core.render_packet(s,'role-001',NOW)['review.md']
        self.assertIn('\\# Send',text);self.assertNotIn('<script>',text)
        self.assertEqual(s,before)

    def test_duplicate_canonical_identity_rejected(self):
        s=self.example();new=copy.deepcopy(s['roles'][0]);new['id']='duplicate';new['title']='Different title';s['roles'].append(new)
        self.assertTrue(any('Duplicate employer' in e for e in core.validate(s,NOW)))

    def test_decline_one_role_does_not_exclude_employer_and_stops_reminder(self):
        s=self.example();r=s['roles'][0]
        s=core.transition(s,'role-001',{'type':'approve','kind':'role_selection','approval_id':'DECLINE-1','actor':'human','decision':'declined','fingerprint':core.role_fingerprint(s,r),'note':'Fictional candidate declines only this role'},NOW)
        self.assertEqual(s['search_brief']['exclusions'],self.example()['search_brief']['exclusions'])
        self.assertEqual(core.due_reminders(s,NOW),[])

    def test_complete_reminder_suppresses_cycle(self):
        s=core.transition(self.example(),'role-001',{'type':'complete_reminder','reminder_id':'REM-001'},NOW)
        self.assertEqual(core.due_reminders(s,NOW),[])

    def test_privacy_scan_detects_common_leaks(self):
        path="/"+"Users/"+"private-fixture/career.docx"
        self.assertIn('Personal absolute home path',checker.privacy_findings(path))
        self.assertIn('Possible API key',checker.privacy_findings('sk'+'-'+('x'*24)))
        self.assertIn('Non-example email address',checker.privacy_findings('candidate'+'@'+'private-fixture.test'))
        self.assertEqual(checker.privacy_findings('avery@example.invalid'),[])

    def test_release_zip_excludes_private_runtime_and_checks_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'kit';root.mkdir()
            (root/'README.md').write_text('[License](LICENSE.md)')
            (root/'LICENSE.md').write_text('Fixture file-based scope.')
            (root/'LICENSE-CODE.txt').write_text('Fixture code license.')
            (root/'LICENSE-CONTENT.txt').write_text('Fixture content license.')
            (root/'NOTICE.txt').write_text('Fixture notice.')
            (root/'.private').mkdir();(root/'.private/workspace.json').write_text('{"private":true}')
            result=checker.build_zip(Path(tmp)/'kit.zip',root)
            self.assertEqual(result['files'],5)
            self.assertFalse(result['published'])
            (root/'README.md').write_text('[Broken](missing.md)')
            self.assertFalse(checker.check(root)['ok'])


if __name__=='__main__':unittest.main()
