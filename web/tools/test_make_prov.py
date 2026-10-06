#!/usr/bin/env python3
"""Unit tests of make_prov.py (web/PLAN-PROV.md). Python 3 stdlib.   python3 web/tools/test_make_prov.py"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_prov as M  # noqa: E402

REG = M.build_registry()


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


class Tokens(unittest.TestCase):
    def t(self, s):
        return M.tokens_of(s)

    def test_claims_and_slash_lists(self):
        self.assertEqual(self.t('c001 D = 169, c031 đoạn 4D/6D'), ['c001', 'c031'])
        self.assertEqual(self.t('c001/c002'), ['c001', 'c002'])
        self.assertEqual(self.t('c053/c055/c056/c057'), ['c053', 'c055', 'c056', 'c057'])

    def test_web_photos(self):
        self.assertEqual(self.t('web-01/02 (khung)'), ['web-01', 'web-02'])
        self.assertEqual(self.t('màu xanh theo web-01/web-03, c023'), ['web-01', 'web-03', 'c023'])

    def test_internal_docs(self):
        self.assertEqual(self.t('pdf_measures §2.2/§4'), ['meas-2.2', 'meas-4'])
        self.assertEqual(self.t('specs §4; design.md §3'), ['spec-4', 'design-3'])
        self.assertEqual(self.t('DECISIONS 9 (1×4D), DECISIONS 11.3 + review-01 M9'), ['dec-9', 'dec-11', 'rev-M9'])
        self.assertEqual(self.t('review-01 I3/I6'), ['rev-I3', 'rev-I6'])
        self.assertEqual(self.t('drawing review-01 I2'), ['drev-I2'])
        self.assertEqual(self.t('ghi chú drafter (design_issues #1)'), ['issue-1'])
        self.assertEqual(self.t('BRIEF (Z = 0 sàn)'), ['brief-coordinate'])

    def test_catalogue_pages_crops_and_images(self):
        self.assertEqual(self.t('hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut)'),
                         ['cat-p12', 'crop-p12_barrel_types_utx_vs_ut_250dpi'])
        self.assertEqual(self.t('p05/p19 (đĩa ly hợp)'), ['cat-p05', 'cat-p19'])
        self.assertEqual(self.t('p08_side_feeder, p06 cutaway'), ['crop-p08_side_feeder_x3', 'cat-p06'])
        self.assertEqual(self.t('p22_5/p23_4 (tấm HMI)'), ['img-p22_5', 'img-p23_4'])
        self.assertEqual(self.t('p24-25 (khung đứng sau trục)'), ['cat-p24'])
        self.assertEqual(self.t('p24-25_slot_die_smoothing_roll'), ['crop-p24-25_slot_die_smoothing_roll_600dpi'])
        self.assertEqual(self.t('p16_1, web-07'), ['img-p16_1', 'web-07'])

    def test_every_parts_source_resolves(self):
        bad = M.unresolved_tokens(REG)
        self.assertEqual(bad, [], f'unresolved tokens: {bad[:10]}')


class Registry(unittest.TestCase):
    def test_counts(self):
        kinds = {}
        for r in REG.values():
            kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
        self.assertEqual(sum(1 for k in REG if k.startswith('c0')), 70)
        self.assertEqual(sum(1 for k in REG if k.startswith('web-')), 20)
        self.assertEqual(sum(1 for k in REG if k.startswith('cat-p')), 30)
        self.assertGreater(kinds['doc'], 50)

    def test_claim_record(self):
        c = M.resolve('c001', REG)
        self.assertEqual(c['kind'], 'claim')
        self.assertEqual(c['value'], 169)
        self.assertIn('yumpu.com', c['url'])
        self.assertIn('169', c['quote'])

    def test_photo_inherits_same_title_and_page(self):
        w2 = M.resolve('web-02', REG)
        w1 = M.resolve('web-01', REG)
        self.assertEqual(w2['title'], w1['title'])
        self.assertTrue(w2['page_url'].startswith('https://'))
        self.assertTrue(os.path.isfile(os.path.join(M.WS, w2['file'])))
        self.assertIn('CC BY-SA', M.resolve('web-11', REG)['credit'] or '')

    def test_catalogue_page(self):
        p = M.resolve('cat-p12', REG)
        self.assertEqual(p['kind'], 'figure')
        self.assertEqual(p['page'], 12)
        self.assertTrue(p['pdf_url'].endswith('ZE_twin-screw_extruders.pdf#page=12'))
        self.assertIn('fine-tuning', p['caption_vi'])
        self.assertEqual(M.resolve('crop-ze155ut_side_600dpi', REG)['page'], 9)
        self.assertEqual(M.resolve('img-p16_1', REG)['page'], 16)

    def test_doc_section_and_pin(self):
        d = M.resolve('spec-1', REG)
        self.assertEqual(d['kind'], 'doc')
        self.assertEqual(d['label'], 'specs.md §1')
        self.assertLessEqual(len(d['excerpt']), 420)
        p = M.resolve('spec-1|Khoảng cách tâm hai trục vít', REG)
        self.assertIn('142', p['excerpt'])
        self.assertNotIn('**', p['excerpt'])
        self.assertIsNone(M.resolve('spec-1|không có chuỗi này', REG))
        self.assertEqual(M.resolve('rev-I2', REG)['excerpt_lang'], 'en')
        self.assertIn('Rear side', M.resolve('rev-I2', REG)['title'])

    def test_denied_and_unknown(self):
        self.assertIsNone(M.resolve('dec-2', REG))
        self.assertIsNone(M.resolve('c999', REG))
        self.assertIsNotNone(M.resolve('dec-9', REG))


class Seed(unittest.TestCase):
    def setUp(self):
        import tempfile
        import shutil
        self.tmp = tempfile.mkdtemp(prefix='prov-seed-')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.devices = M.load_devices()

    def test_device_lines(self):
        lines = M.device_lines(self.devices)
        self.assertEqual(len(lines), 534)
        self.assertEqual(len({M.line_key(x['vi']) for x in lines}), 454)
        self.assertEqual(lines[0]['kind'], 'function')
        self.assertFalse(any(x['device'].startswith('x_') for x in lines))

    def test_seed_writes_groups_and_is_idempotent(self):
        M.seed(self.devices, self.tmp)
        files = sorted(os.listdir(self.tmp))
        self.assertEqual(len(files), 10)
        entries = {}
        for f in files:
            entries.update(M.load_json(os.path.join(self.tmp, f))['lines'])
        self.assertEqual(len(entries), 454)
        self.assertEqual(sum(len(e['used_by']) for e in entries.values()), 534)
        b3 = entries[M.line_key(next(d for d in self.devices if d['device_id'] == 'barrel_b3')['function_vi'])]
        self.assertEqual(b3['status'], 'draft')
        self.assertIn('barrel_b3:function', b3['used_by'])
        self.assertIn('c001', b3['seed']['refs'])
        before = {f: read_bytes(os.path.join(self.tmp, f)) for f in files}
        M.seed(self.devices, self.tmp)
        self.assertEqual(before, {f: read_bytes(os.path.join(self.tmp, f)) for f in files})

    def test_seed_keeps_curated_facts(self):
        M.seed(self.devices, self.tmp)
        path = os.path.join(self.tmp, 'barrel.json')
        doc = M.load_json(path)
        key = next(iter(doc['lines']))
        doc['lines'][key].update(status='curated', facts=[{'level': 'assumption', 'text_vi': 'x'}], notes='n')
        M.save_lines(path, doc)
        M.seed(self.devices, self.tmp)
        e = M.load_json(path)['lines'][key]
        self.assertEqual((e['status'], e['facts'][0]['text_vi'], e['notes']), ('curated', 'x', 'n'))


class Images(unittest.TestCase):
    def test_thumb_and_large(self):
        import shutil
        import tempfile
        tmp = tempfile.mkdtemp(prefix='prov-img-')
        self.addCleanup(shutil.rmtree, tmp, True)
        for rid in ('web-02', 'crop-p12_barrel_types_utx_vs_ut_250dpi'):
            d = M.make_images(M.resolve(rid, REG), tmp)
            self.assertEqual(max(d['t']), 480)
            self.assertLessEqual(max(d['l']), 1280)
            self.assertTrue(os.path.isfile(os.path.join(tmp, f'{rid}.t.jpg')))


B3_FIGURE8 = 'Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71).'
GOOD_FACTS = [
    {'level': 'sourced', 'text_vi': 'Ø169: đường kính vít ZE 155 A UTi theo bảng KM',
     'text_ja': 'Ø169:KM 技術データ表による ZE 155 A UTi のスクリュー径', 'refs': ['c001']},
    {'level': 'derived', 'text_vi': 'Lỗ hình số 8 (2 lỗ giao nhau): rộng 311 = a 142 + D 169, tâm Y = ±71 = a/2',
     'text_ja': '8の字穴(2つの穴が重なる):幅 311 = a 142 + D 169、中心 Y = ±71 = a/2',
     'refs': ['spec-1|Khoảng cách tâm hai trục vít'], 'reason_vi': 'a = (D + d)/2 ≈ 142', 'reason_ja': 'a = (D + d)/2 ≈ 142'},
]


class Check(unittest.TestCase):
    """also the negative cases of `make prov-negative` (PLAN-PROV Task 3)"""

    def setUp(self):
        import copy
        import shutil
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix='prov-check-')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.devices = M.load_devices()
        M.seed(self.devices, os.path.join(self.tmp, 'lines'))
        self.key = M.line_key(B3_FIGURE8)
        self.facts = copy.deepcopy(GOOD_FACTS)
        self.edit(lambda e: e.update(status='curated', facts=self.facts))

    def edit(self, fn):
        path = os.path.join(self.tmp, 'lines', 'barrel.json')
        doc = M.load_json(path)
        fn(doc['lines'][self.key])
        M.save_lines(path, doc)

    def codes(self, strict=False, i18n=None):
        r = M.check(self.devices, os.path.join(self.tmp, 'lines'), REG, i18n or {}, strict)
        return sorted({f['code'] for f in r['failures'] if f['key'] == self.key})

    def test_good_entry_passes(self):
        self.assertEqual(self.codes(), [])
        self.assertEqual(self.codes(strict=True), ['P04', 'P14'])
        self.assertEqual(self.codes(strict=True, i18n={'spec-1': {'title_ja': '仕様 §1'}}), ['P04'])

    def test_edited_text_is_drift(self):
        self.edit(lambda e: e.update(vi=e['vi'].replace('311', '312')))
        self.assertIn('P02', self.codes())

    def test_unknown_ref(self):
        self.facts[0]['refs'] = ['c999']
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P06', self.codes())

    def test_sourced_needs_public_evidence(self):
        self.facts[0]['refs'] = ['spec-1']
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P07', self.codes())

    def test_assumption_needs_reason(self):
        self.facts[1] = dict(self.facts[1], level='assumption', reason_ja='')
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P09', self.codes())

    def test_japanese_missing_or_vietnamese(self):
        del self.facts[0]['text_ja']
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P10', self.codes())
        self.facts[0]['text_ja'] = 'đường kính vít'
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P10', self.codes())

    def test_denied_strings(self):
        self.facts[0]['text_vi'] += ' (22_3_160)'
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertIn('P13', self.codes())

    def test_every_number_needs_a_fact_in_strict(self):
        self.facts[1]['text_vi'] = self.facts[1]['text_vi'].replace(', tâm Y = ±71 = a/2', '')
        self.edit(lambda e: e.update(facts=self.facts))
        self.assertNotIn('P11', self.codes())
        self.assertIn('P11', self.codes(strict=True))
        self.edit(lambda e: e.update(free_numbers=['71']))
        self.assertNotIn('P11', self.codes(strict=True))

    def test_numbers_ignore_names(self):
        self.assertEqual(M.numbers_in('Xi lanh B5, bulông M24, PT100, X = 1 890, Ø520 × 2,5'), {'1890', '520', '2,5'})

    def test_build_output(self):
        out = os.path.join(self.tmp, 'out')
        r = M.build(self.devices, os.path.join(self.tmp, 'lines'), REG, {}, False, out, images=False)
        self.assertTrue(r['ok'], r['failures'][:3])
        files = [f for f in os.listdir(out) if f.endswith('.json')]
        self.assertEqual(len(files), 186)
        d = M.load_json(os.path.join(out, 'barrel_b3.json'))
        ln = next(x for x in d['lines'] if x['vi'] == B3_FIGURE8)
        self.assertEqual((ln['kind'], ln['index'], ln['level']), ('details', 2, 'derived'))
        self.assertEqual(d['lines'][0]['level'], None)
        self.assertEqual(d['lines'][0]['facts'], [])
        self.assertIn('142', d['sources']['spec-1|Khoảng cách tâm hai trục vít']['excerpt'])
        self.assertEqual(d['sources']['c001']['kind'], 'claim')
        self.assertNotIn('units', json.dumps(d))


if __name__ == '__main__':
    unittest.main(verbosity=1)
