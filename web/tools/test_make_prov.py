#!/usr/bin/env python3
"""Unit tests of make_prov.py (web/PLAN-PROV.md). Python 3 stdlib.   python3 web/tools/test_make_prov.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_prov as M  # noqa: E402

REG = M.build_registry()


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


if __name__ == '__main__':
    unittest.main(verbosity=1)
