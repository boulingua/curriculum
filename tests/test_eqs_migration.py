from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_eqs import migrate, read, write, activation_split


class Migration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name)
        self.unit=self.repo/'content/course/unit/index.md';self.unit.parent.mkdir(parents=True)
        self.body='\n'+''.join('## '+h+'\n\nLearner task.\n\n' for h in ['1. Activate','2. Input','3. Practise','4. Produce','5. Reflect'])+'## Exam example\n\nOriginal task and answer.\n\n## Downloads\n\nTeacher guidance.\n'
        self.unit.write_text(write({'page_type':'unit','title':'One','aliases':['/original.html'],'curriculum':{'level':'A1','implements':['A1.INT.conversation.01'],'implements_basis':'proposed'}},self.body))
        self.exam=self.repo/'content/course/unit-exam/index.md';self.exam.parent.mkdir()
        self.exam.write_text(write({'page_type':'exam'},'\nOriginal task and answer.\n'))
        html=self.repo/'public/course/unit/index.html';html.parent.mkdir(parents=True);html.write_text(''.join(f'<h2 id="{key}">{label}<a class="heading-link"><span>Link to heading</span></a></h2>' for key,label in [('old-activate','1. Activate'),('old-input','2. Input'),('old-practise','3. Practise'),('former-produce','4. Produce'),('old-reflect','5. Reflect'),('old-exam','Exam example')]))
    def tearDown(self):self.temp.cleanup()
    def test_exact_task_is_removed_only_when_present_in_sibling(self):
        changes,ledger=migrate(self.repo,'efl');fm,body=read(changes[self.unit][1])
        self.assertNotIn('Original task and answer.',body)
        self.assertIn('Original task and answer.',self.exam.read_text())
        self.assertEqual(fm['aliases'],['/original.html'])
        self.assertEqual(fm['anchor_aliases']['apply'],['former-produce'])
        self.assertEqual(fm['curriculum']['implements_basis'],'proposed')
        self.assertIn('Teacher guidance.',body)
        self.assertTrue(ledger[0]['exact_existing_assessment'])
    def test_divergent_task_stays_until_individual_review(self):
        self.exam.write_text(write({'page_type':'exam'},'Different assessment.\n'))
        changes,ledger=migrate(self.repo,'efl')
        self.assertIn('Original task and answer.',changes[self.unit][1])
        self.assertNotIn(self.exam,changes)
        self.assertTrue(any('differ' in x for x in ledger[0]['pending']))
    def test_no_existing_render_cannot_guess_legacy_anchors(self):
        (self.repo/'public/course/unit/index.html').unlink()
        with self.assertRaises(ValueError):migrate(self.repo,'efl')
    def test_existing_activation_task_is_promoted_without_rewriting(self):
        body='Story with dialogue.\n\n**Fragen zum Einstieg:**\n\n- What do you know?\n'
        story,task=activation_split(body)
        self.assertEqual(story+task,body)
        self.assertIn('What do you know?',task)
        with self.assertRaises(ValueError):activation_split('A story with no learner task.')


if __name__=='__main__':unittest.main()
