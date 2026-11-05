from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import contextlib
import io
import sys
import tempfile
import unittest
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import conformance_audit as audit

ID='A1.REC.overall-reading-comprehension.01'


class Resolution(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.content=self.root/'content';self.content.mkdir()
        self.page=self.content/'lesson.md'
        self.page.write_text(f'---\ncurriculum:\n  level: A1\n  implements: [{ID}]\n  implements_basis: proposed\n---\nA lesson.\n')
        self.man={'framework':'boulingua-curriculum','framework_version':(Path(__file__).resolve().parents[1]/'VERSION').read_text().strip(),'language':'en','declared_conformance':'core','conformance_status':'in-progress','realizations':[{'implements_id':ID,'page':'lesson'}]}
        self.path=self.root/'curriculum.yml'
        self.pending_reviews=[]
    def tearDown(self):self.temp.cleanup()
    def resolve(self, content=True):
        self.path.write_text(yaml.safe_dump(self.man))
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()), patch.object(audit,'pending_source_reviews',return_value=self.pending_reviews):
            return audit.cmd_resolve(SimpleNamespace(manifest=self.path,content=self.content if content else None))
    def test_in_progress_correct_mapping(self):self.assertEqual(self.resolve(),0)
    def test_wrong_page_cannot_hide_behind_same_global_id(self):
        self.man['realizations'][0]['page']='different';self.assertEqual(self.resolve(),4)
    def test_manifest_only_mapping_fails(self):
        self.page.write_text('---\ntitle: No mapping\n---\n'+ID+' only in prose.\n');self.assertEqual(self.resolve(),4)
    def test_content_only_mapping_fails(self):
        self.man['realizations']=[];self.assertEqual(self.resolve(),4)
    def test_duplicate_pair_fails_but_descriptor_can_be_reused(self):
        self.man['realizations']*=2;self.assertEqual(self.resolve(),3)
        self.man['realizations'][1]={'implements_id':ID,'page':'second'}
        (self.content/'second.md').write_text(self.page.read_text());self.assertEqual(self.resolve(),0)
    def test_bad_descriptor_blocks_even_in_progress(self):
        self.man['realizations'][0]['implements_id']='A1.REC.unknown.01';self.assertEqual(self.resolve(),3)
    def test_met_cannot_use_proposed_mappings(self):
        self.man['conformance_status']='met'
        with patch.object(audit,'load_empty_scales',return_value={}), patch.object(audit,'cells',return_value=({'A1':{('REC','overall-reading-comprehension')}},{})):
            self.assertEqual(self.resolve(),5)
    def test_threshold_rounds_up_and_gaps_must_be_declared(self):
        self.man['conformance_status']='met';self.page.write_text(self.page.read_text().replace('proposed','asserted'))
        with patch.object(audit,'load_empty_scales',return_value={}), patch.object(audit,'cells',return_value=({'A1':{('REC','overall-reading-comprehension')}},{})):
            self.assertEqual(self.resolve(),0)
        with patch.object(audit,'cells',return_value=({'A1':{('REC','overall-reading-comprehension'),('REC','other')}},{})):
            self.assertEqual(self.resolve(),5)
    def test_restricted_profile_requires_latin_and_approved_profile(self):
        self.man['declared_conformance']='core-restricted';self.assertEqual(self.resolve(),2)
        self.man['profile']='classical-reception';self.assertEqual(self.resolve(),2)
        self.man['language']='la';self.assertEqual(self.resolve(),0)
    def test_missing_content_is_failure(self):
        self.page.unlink();self.content.rmdir();self.assertEqual(self.resolve(),4)
    def test_manifest_shape_and_unknown_fields_fail_cleanly(self):
        self.man['realizations']='not a list';self.assertEqual(self.resolve(),2)
        self.man['realizations']=[];self.man['mistyped_status']='met';self.assertEqual(self.resolve(),2)
    def test_source_level_must_match_descriptor(self):
        self.page.write_text(self.page.read_text().replace('level: A1','level: A2'));self.assertEqual(self.resolve(),3)
    def test_path_traversal_is_not_a_content_page(self):
        self.man['realizations'][0]['page']='../outside';self.assertEqual(self.resolve(),3)
    def test_known_framework_omission_prevents_met_claim(self):
        self.man['conformance_status']='met'
        self.page.write_text(self.page.read_text().replace('proposed','asserted'))
        with patch.object(audit,'load_empty_scales',return_value={('INT','co-operating'):{'status':'missing-in-repository','source_levels':['A2']}}), patch.object(audit,'cells',return_value=({'A1':{('REC','overall-reading-comprehension')}},{})):
            self.assertEqual(self.resolve(),5)
    def test_framework_version_is_exact(self):
        self.man['framework_version']='1.1.0';self.assertEqual(self.resolve(),6)
    def test_restored_but_unreviewed_source_blocks_only_achieved_claim(self):
        self.pending_reviews=[{'new_ids':['A2.INT.co-operating.01']}]
        self.assertEqual(self.resolve(),0)
        self.man['conformance_status']='met'
        self.assertEqual(self.resolve(),5)


class SourceIntegrity(unittest.TestCase):
    def test_restored_scales_have_the_source_rows_at_each_level(self):
        statements=audit.load_statements()
        expected={'PROD.addressing-audiences':{'A1':1,'A2':4,'B1':3,'B2':4,'C1':4,'C2':2},
                  'INT.co-operating':{'A2':1,'B1':4,'B2':4,'C1':1,'C2':1}}
        for key,levels in expected.items():
            rows=[s for s in statements if '.'.join(s['id'].split('.')[1:3])==key]
            self.assertEqual({lv:sum(s['implements']['level']==lv for s in rows) for lv in audit.LEVELS if any(s['implements']['level']==lv for s in rows)},levels)
            self.assertTrue(all(s['implements'].get('source_page') in {65,66,88,89} for s in rows))
        b2=[s['implements'] for s in statements if s['id'].startswith('B2.INT.co-operating.')]
        self.assertEqual([(r['source_level'],r['source_ordinal']) for r in b2],[('B2+',1),('B2+',2),('B2',1),('B2',2)])
    def test_pending_omission_is_never_a_coverage_exemption(self):
        with patch.object(audit,'load_empty_scales',return_value={('INT','co-operating'):{'status':'missing-in-repository'}}):
            self.assertEqual(audit.load_excused(),{})


if __name__=='__main__':unittest.main()
