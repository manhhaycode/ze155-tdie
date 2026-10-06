#!/usr/bin/env python3
"""make_prov.py - sources of the info-panel lines (web/PLAN-PROV.md). Python 3; PIL only for `build` images.

    python3 tools/make_prov.py registry      -> build/prov/registry.json (ref ids of PLAN-PROV §2.1)
    python3 tools/make_prov.py selftest      every reference token in design/parts.json `source` resolves

Inputs: research/claims.jsonl, research/web/images.md (+ img/), research/pages, research/pdf_crops,
research/pdf_images, research/pdf_catalog.md, research/specs.md, research/pdf_measures.md, design/design.md,
anim/design-anim.md, DECISIONS.md, design/review-01.md, drawings/review-01.md, drawings/design_issues.md, BRIEF.md.
Writes only under web/build/ (like make_data.py).
"""
import argparse
import json
import os
import re
import sys

WEB = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
WS = os.path.dirname(WEB)
BUILD = os.path.join(WEB, 'build')
PDF_URL = 'https://plastrading.com/wp-content/uploads/2018/03/ZE_twin-screw_extruders.pdf'
CATALOGUE_PAGES = 30
# DECISIONS #2 is about a document of the user that never goes on the web
DENY_REFS = {'dec-2'}
EXCERPT_MAX = 400
PIN_MAX = 500


def read(rel):
    with open(os.path.join(WS, rel), encoding='utf-8') as f:
        return f.read()


def clean_md(s):
    """one markdown line -> plain text (table cells joined with ' · ')"""
    s = s.strip()
    if s.startswith('|') and s.endswith('|'):
        s = ' · '.join(c.strip() for c in s.strip('|').split('|') if c.strip())
    s = re.sub(r'^(?:[-*]|\d+\.)\s+', '', s)
    s = s.replace('**', '').replace('`', '').replace('<br>', ' ')
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()


def clip(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + '…'


def units_of(lines):
    """the pinnable units of a section: each non-empty, non-separator line"""
    return [u for u in (clean_md(x) for x in lines if not re.match(r'^\s*\|?\s*-{3}', x)) if u]


def doc_record(rid, label, title, lines, lang):
    units = units_of(lines)
    return {'kind': 'doc', 'id': rid, 'label': label, 'title': title, 'excerpt_lang': lang,
            'excerpt': clip(' / '.join(units), EXCERPT_MAX), 'units': units}


# ---------------------------------------------------------------- documents
def numbered_sections(rel, prefix, label_fmt, lang):
    """`## 1. Title` / `### 2.2 Title` -> {prefix-1, prefix-2.2}; a section ends at the next heading"""
    out, cur, body = {}, None, []

    def flush():
        if cur:
            num, title = cur
            rid = f'{prefix}-{num}'
            out[rid] = doc_record(rid, label_fmt.format(num), title, body, lang)

    for line in read(rel).splitlines():
        m = re.match(r'^#{2,4}\s+(.*)$', line)
        if m:
            flush()
            body = []
            n = re.match(r'^(\d+(?:\.\d+)*)\.?\s+(.*)$', m.group(1))
            cur = (n.group(1), clean_md(n.group(2))) if n else None
            continue
        if cur:
            body.append(line)
    flush()
    return out


def review_sections(rel, prefix, label):
    """`### I2. Title` -> {prefix-I2}"""
    out, cur, body = {}, None, []

    def flush():
        if cur:
            rid = f'{prefix}-{cur[0]}'
            out[rid] = doc_record(rid, f'{label} {cur[0]}', cur[1], body, 'en')

    for line in read(rel).splitlines():
        m = re.match(r'^#{2,4}\s+(.*)$', line)
        if m:
            flush()
            body = []
            n = re.match(r'^([CIM]\d+)\.\s+(.*)$', m.group(1))
            cur = (n.group(1), clean_md(n.group(2))) if n else None
            continue
        if cur:
            body.append(line)
    flush()
    return out


def decisions():
    """numbered items `N. **Title:** ...` of DECISIONS.md, continuation lines indented"""
    out, cur, body = {}, None, []

    def flush():
        if cur:
            rid = f'dec-{cur[0]}'
            out[rid] = doc_record(rid, f'DECISIONS.md #{cur[0]}', cur[1], body, 'vi')

    for line in read('DECISIONS.md').splitlines():
        m = re.match(r'^(\d+)\.\s+(.*)$', line)
        if m:
            flush()
            t = re.match(r'\*\*(.+?)\*\*\s*(.*)$', m.group(2))
            title = clean_md(t.group(1)).rstrip(':') if t else clean_md(m.group(2))[:80]
            cur, body = (m.group(1), title), ([t.group(2)] if t and t.group(2) else [])
        elif line.startswith('#'):
            flush()
            cur, body = None, []
        elif cur:
            body.append(line)
    flush()
    return out


def design_issues():
    out = {}
    for line in read('drawings/design_issues.md').splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|\s*([^|]*)\|\s*([^|]*)\|', line)
        if m:
            rid = f'issue-{m.group(1)}'
            out[rid] = doc_record(rid, f'drawings/design_issues.md #{m.group(1)}', clean_md(m.group(3))[:90], [line], 'vi')
    return out


def brief():
    out, cur, body = {}, None, []

    def flush():
        if cur:
            rid = f'brief-{cur.split()[0].lower()}'
            out[rid] = doc_record(rid, f'BRIEF.md – {cur}', cur, body, 'en')

    for line in read('BRIEF.md').splitlines():
        m = re.match(r'^##\s+(.*)$', line)
        if m:
            flush()
            cur, body = clean_md(m.group(1)), []
        elif cur:
            body.append(line)
    flush()
    return out


# ---------------------------------------------------------------- claims, photos, catalogue
def claims():
    out = {}
    for line in read('research/claims.jsonl').splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        title = re.sub(r',?\s*local copy \S+', '', c['source_title']).strip()
        out[c['id']] = {'kind': 'claim', 'id': c['id'], 'title': title, 'url': c['source_url'], 'quote': c['quote'],
                        'claim': c['claim'], 'value': c['value'], 'unit': c['unit'], 'confidence': c['confidence'],
                        'topic': c['topic']}
    return out


def photos():
    rows = []
    for line in read('research/web/images.md').splitlines():
        if re.match(r'^\|\s*web-\d{2}\.jpg', line):
            rows.append([c.strip() for c in line.strip().strip('|').split('|')])
    out, prev, brochure = {}, None, None
    for f, src, title, shows, _angle, _parts, _colours, brand in rows:
        rid = f[:-4]
        same_as = re.match(r'same as (web-\d{2})', title)
        base = out[same_as.group(1)] if same_as else prev
        if title.startswith('same'):
            title = base['title']
        title = re.sub(r'\s*\(".*"\)$', '', title)
        image_url, page_url, credit = None, None, None
        emb = re.match(r'(?:Embedded image|Crop of page), page (\d+) of (.*)$', src) or re.match(r'Crop of page (\d+) of (\S+)', src)
        if emb:
            url = emb.group(2)
            brochure = brochure if url.startswith('the same') else url
            page_url = f'{brochure}#page={emb.group(1)}'
        else:
            m = re.match(r'(\S+)\s*(?:\((.*)\))?$', src)
            image_url, paren = m.group(1), (m.group(2) or '')
            pm = re.match(r'page (\S+?),?(?:\s|$)', paren)
            page_url = pm.group(1) if pm else base['page_url']
            if 'CC BY' in paren:
                credit = 'Wikimedia Commons, ' + re.search(r'CC BY[-\w. ]*', paren).group(0).strip()
        out[rid] = {'kind': 'photo', 'id': rid, 'title': title, 'page_url': page_url, 'image_url': image_url,
                    'shows_en': shows, 'brand': brand, 'credit': credit, 'file': f'research/web/img/{f}'}
        prev = out[rid]
    return out


def page_captions():
    caps = {}
    for line in read('research/pdf_catalog.md').splitlines():
        m = re.match(r'^###\s+Trang\s+(\d+)(?:[–-](\d+))?\s*[–-]\s*(.*)$', line)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            for p in range(a, b + 1):
                caps[p] = clean_md(line[4:])
    return caps


def page_of(stem):
    if re.match(r'ze\d{3}ut', stem):
        return 9
    return int(re.match(r'p(\d{2})', stem).group(1))


def figures():
    caps, out = page_captions(), {}

    def rec(rid, page, rel):
        return {'kind': 'figure', 'id': rid, 'page': page, 'pdf_url': f'{PDF_URL}#page={page}',
                'caption_vi': caps.get(page, f'Trang {page}'), 'file': rel}

    for p in range(1, CATALOGUE_PAGES + 1):
        out[f'cat-p{p:02d}'] = rec(f'cat-p{p:02d}', p, f'research/pages/p{p:02d}.png')
    for f in sorted(os.listdir(os.path.join(WS, 'research/pdf_crops'))):
        stem, ext = os.path.splitext(f)
        if ext == '.png':
            out[f'crop-{stem}'] = rec(f'crop-{stem}', page_of(stem), f'research/pdf_crops/{f}')
    for f in sorted(os.listdir(os.path.join(WS, 'research/pdf_images'))):
        stem, ext = os.path.splitext(f)
        if ext in ('.jpeg', '.jpg', '.png'):
            out[f'img-{stem}'] = rec(f'img-{stem}', page_of(stem), f'research/pdf_images/{f}')
    return out


def build_registry():
    reg = {}
    reg.update(claims())
    reg.update(photos())
    reg.update(figures())
    reg.update(numbered_sections('research/specs.md', 'spec', 'specs.md §{}', 'vi'))
    reg.update(numbered_sections('research/pdf_measures.md', 'meas', 'pdf_measures.md §{}', 'vi'))
    reg.update(numbered_sections('design/design.md', 'design', 'design.md §{}', 'vi'))
    reg.update(numbered_sections('anim/design-anim.md', 'anim', 'design-anim.md §{}', 'vi'))
    reg.update(decisions())
    reg.update(review_sections('design/review-01.md', 'rev', 'design/review-01.md'))
    reg.update(review_sections('drawings/review-01.md', 'drev', 'drawings/review-01.md'))
    reg.update(design_issues())
    reg.update(brief())
    return reg


def resolve(ref, reg):
    """a ref id (optionally `doc-id|pin`) -> its public record, or None (unknown, denied, pin not unique)"""
    rid, _, pin = ref.partition('|')
    base = reg.get(rid)
    if base is None or rid in DENY_REFS:
        return None
    rec = {k: v for k, v in base.items() if k != 'units'}
    if pin:
        if base['kind'] != 'doc':
            return None
        hits = [u for u in base['units'] if pin in u]
        if len(hits) != 1:
            return None
        rec['excerpt'] = clip(hits[0], PIN_MAX)
        rec['pin'] = pin
    return rec


# ---------------------------------------------------------------- reference tokens of parts.json `source`
TOKEN = re.compile(
    r'(?P<drev>drawing review-01 (?P<drev_l>[CIM]\d+(?:/[CIM]?\d+)*))'
    r'|(?P<rev>review-01 (?P<rev_l>[CIM]\d+(?:/[CIM]?\d+)*))'
    r'|(?P<dec>DECISIONS\s*#?(?P<dec_n>\d+)(?:\.\d+)?)'
    r'|(?P<issue>design_issues\s*#(?P<issue_n>\d+))'
    r'|(?P<anim>design-anim(?:\.md)?\s*§(?P<anim_n>\d+(?:\.\d+)*))'
    r'|(?P<design>design(?:\.md)?\s*§(?P<design_n>\d+(?:\.\d+)*))'
    r'|(?P<meas>pdf_measures(?:\.md)?\s*§(?P<meas_l>\d+(?:\.\d+)*(?:/§?\d+(?:\.\d+)*)*))'
    r'|(?P<spec>specs(?:\.md)?\s*§(?P<spec_l>\d+(?:\.\d+)*(?:/§?\d+(?:\.\d+)*)*))'
    r'|(?P<brief>\bBRIEF\b)'
    r'|(?P<claim>\bc(?P<claim_n>\d{3})\b)'
    r'|(?P<web>\bweb-(?P<web_l>\d{2}(?:/\d{2}\b)*))'
    r'|(?P<trang>\btrang (?P<trang_n>\d+))'
    r'|(?P<page>\bp(?P<page_n>\d{2})(?:[-–]\d{2})?(?P<page_s>(?:_[a-z0-9]+)*))'
)
_CROPS = None


def _crop_stems():
    global _CROPS
    if _CROPS is None:
        _CROPS = sorted(os.path.splitext(f)[0] for f in os.listdir(os.path.join(WS, 'research/pdf_crops')) if f.endswith('.png'))
    return _CROPS


def _letter_list(s):
    """'I3/I6' -> [I3, I6]; 'C1/2' -> [C1, C2]"""
    out, letter = [], ''
    for p in s.split('/'):
        if p[0].isalpha():
            letter = p[0]
            out.append(p)
        else:
            out.append(letter + p)
    return out


def _page_token(m):
    n, suffix, whole = m.group('page_n'), m.group('page_s'), m.group('page')
    if not suffix:
        return f'cat-p{n}'
    stem = whole
    if os.path.exists(os.path.join(WS, 'research/pdf_images', stem + '.jpeg')) or \
            os.path.exists(os.path.join(WS, 'research/pdf_images', stem + '.png')):
        return f'img-{stem}'
    hits = [s for s in _crop_stems() if s == stem or s.startswith(stem + '_')]
    return f'crop-{hits[0]}' if len(hits) == 1 else f'crop-{stem}?'


def tokens_of(source):
    out = []

    def add(t):
        if t not in out:
            out.append(t)

    for m in TOKEN.finditer(source):
        k = next(g for g in ('drev', 'rev', 'dec', 'issue', 'anim', 'design', 'meas', 'spec', 'brief', 'claim', 'web', 'trang', 'page') if m.group(g))
        if k == 'drev':
            [add(f'drev-{x}') for x in _letter_list(m.group('drev_l'))]
        elif k == 'rev':
            [add(f'rev-{x}') for x in _letter_list(m.group('rev_l'))]
        elif k == 'dec':
            add(f'dec-{m.group("dec_n")}')
        elif k == 'issue':
            add(f'issue-{m.group("issue_n")}')
        elif k == 'anim':
            add(f'anim-{m.group("anim_n")}')
        elif k == 'design':
            add(f'design-{m.group("design_n")}')
        elif k in ('meas', 'spec'):
            prefix = 'meas' if k == 'meas' else 'spec'
            [add(f'{prefix}-{x.lstrip("§")}') for x in m.group(f'{k}_l').split('/')]
        elif k == 'brief':
            add('brief-coordinate')
        elif k == 'claim':
            add(f'c{m.group("claim_n")}')
        elif k == 'web':
            [add(f'web-{x}') for x in m.group('web_l').split('/')]
        elif k == 'trang':
            add(f'cat-p{int(m.group("trang_n")):02d}')
        else:
            add(_page_token(m))
    return out


def parts():
    with open(os.path.join(WS, 'design/parts.json'), encoding='utf-8') as f:
        return json.load(f)['parts']


def unresolved_tokens(reg):
    bad = []
    for p in parts():
        for t in tokens_of(p.get('source', '')):
            if resolve(t, reg) is None:
                bad.append(f'{p["id"]}: {t}')
    return bad


# ---------------------------------------------------------------- lines of the info panel and the curated files
LINES = os.path.join(WEB, 'prov', 'lines')
DEVICES = os.path.join(BUILD, 'data', 'devices.json')
ENTRY_ORDER = ['vi', 'used_by', 'status', 'facts', 'free_numbers', 'seed', 'notes', 'verified']


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_devices(path=DEVICES):
    return load_json(path)['devices']


def line_key(vi):
    import hashlib
    return hashlib.sha1(vi.encode('utf-8')).hexdigest()[:12]


def device_lines(devices):
    """every line the info panel shows: the function (index 0) and the details of each non-synthetic device"""
    out = []
    for d in devices:
        if d.get('synthetic'):
            continue
        if d.get('function_vi'):
            out.append({'device': d['device_id'], 'group': d['group'], 'kind': 'function', 'index': 0, 'vi': d['function_vi']})
        for i, t in enumerate(d.get('details_vi') or []):
            out.append({'device': d['device_id'], 'group': d['group'], 'kind': 'details', 'index': i, 'vi': t})
    return out


def use_id(ln):
    return f'{ln["device"]}:function' if ln['kind'] == 'function' else f'{ln["device"]}:details[{ln["index"]}]'


def save_lines(path, doc):
    doc['lines'] = {k: {f: e[f] for f in ENTRY_ORDER if f in e} for k, e in doc['lines'].items()}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')


def seed(devices, lines_dir=LINES):
    """create or refresh web/prov/lines/<group>.json: one entry per unique line, keyed by line_key(vi).
    Refreshes `vi`, `used_by` and `seed` (hints: the parts.json source strings and their ref ids); never
    touches `status`, `facts`, `free_numbers`, `notes`, `verified`. Entries no device uses any more stay
    (check reports them, P03)."""
    reg = build_registry()
    src = {p['id']: p.get('source', '') for p in parts()}
    groups = {}
    for ln in device_lines(devices):
        k = line_key(ln['vi'])
        for g, es in groups.items():
            if g != ln['group'] and k in es:
                raise SystemExit(f'line {k} is used by two groups ({g}, {ln["group"]}): {ln["vi"][:60]}')
        e = groups.setdefault(ln['group'], {}).setdefault(k, {'vi': ln['vi'], 'used_by': [], 'sources': []})
        e['used_by'].append(use_id(ln))
        s = src.get(ln['device'], '')
        if s and s not in e['sources']:
            e['sources'].append(s)
    os.makedirs(lines_dir, exist_ok=True)
    for g, es in groups.items():
        path = os.path.join(lines_dir, f'{g}.json')
        doc = load_json(path) if os.path.exists(path) else {'version': 1, 'group': g, 'lines': {}}
        old = doc['lines']
        new = {}
        for k, e in es.items():
            refs = []
            for s in e['sources']:
                refs += [t for t in tokens_of(s) if t not in refs and resolve(t, reg)]
            cur = old.get(k, {'status': 'draft', 'facts': [], 'notes': ''})
            cur.update(vi=e['vi'], used_by=e['used_by'], seed={'sources': e['sources'], 'refs': refs})
            new[k] = cur
        for k, e in old.items():
            new.setdefault(k, e)
        doc['lines'] = new
        save_lines(path, doc)
    return groups


# ---------------------------------------------------------------- check (PLAN-PROV §2.4)
LEVELS = ('assumption', 'derived', 'sourced')  # weakest first
PUBLIC_EVIDENCE = ('claim', 'figure', 'photo')
DENY_STRINGS = ('22_3_160', 'ideathon', '/Users/', '~/')
DEVICE_MAX_BYTES = 64 * 1024
NUMBER = re.compile(r'(?<![A-Za-z\d,.])\d{1,3}(?:[   ]\d{3})+(?:,\d+)?(?![\d])|(?<![A-Za-z\d,.])\d+(?:,\d+)?')
KANA_KANJI = re.compile(r'[぀-ヿ㐀-鿿]')
VI_TONES = {'̀', '́', '̃', '̉', '̣'}


def numbers_in(text):
    """the stand-alone numbers of a line ('1 890' -> '1890'); a number right after a Latin letter is a name (B5, M24)"""
    return {re.sub(r'[   ]', '', m) for m in NUMBER.findall(text)}


def has_vietnamese(text):
    import unicodedata
    for ch in text:
        if ch in 'ăâđêôơưĂÂĐÊÔƠƯ':
            return True
        if any(c in VI_TONES for c in unicodedata.normalize('NFD', ch)[1:]) and ch.isalpha() and ord(ch) < 0x2000:
            return True
    return False


def weakest(facts):
    return min((f['level'] for f in facts), key=LEVELS.index)


def load_entries(lines_dir):
    """{key: (group, entry)}, plus the duplicate keys"""
    out, dup = {}, []
    for f in sorted(os.listdir(lines_dir)):
        if not f.endswith('.json'):
            continue
        doc = load_json(os.path.join(lines_dir, f))
        for k, e in doc['lines'].items():
            if k in out:
                dup.append(k)
            out[k] = (doc['group'], e)
    return out, dup


def check(devices, lines_dir, reg, i18n, strict):
    fails, warns = [], []

    def fail(code, key, detail, device=None):
        fails.append({'code': code, 'key': key, 'device': device, 'detail': detail})

    entries, dup = load_entries(lines_dir)
    for k in dup:
        fail('P01', k, 'key in two group files')
    used = set()
    for ln in device_lines(devices):
        k = line_key(ln['vi'])
        used.add(k)
        if k not in entries:
            fail('P01', k, f'no entry for {use_id(ln)}: {ln["vi"][:60]}', ln['device'])
    for k, (g, e) in entries.items():
        vi = e.get('vi', '')
        if line_key(vi) != k:
            fail('P02', k, f'text changed (key of the text is {line_key(vi)}): {vi[:60]}')
        if strict and k not in used:
            fail('P03', k, f'no device shows this line any more: {vi[:60]}')
        status = e.get('status', 'draft')
        if strict and status != 'verified':
            fail('P04', k, f'status {status}')
        if status == 'draft':
            continue
        facts = e.get('facts') or []
        if not facts:
            fail('P05', k, 'no facts')
            continue
        for i, f in enumerate(facts):
            where = f'fact {i}'
            if f.get('level') not in LEVELS:
                fail('P05', k, f'{where}: level {f.get("level")!r}')
                continue
            if not f.get('text_vi'):
                fail('P05', k, f'{where}: no text_vi')
            kinds = []
            for r in f.get('refs') or []:
                rec = resolve(r, reg)
                if rec is None:
                    fail('P06', k, f'{where}: ref {r!r} does not resolve (unknown, denied or pin not unique)')
                else:
                    kinds.append(rec['kind'])
                    if f['level'] == 'sourced' and rec['kind'] == 'claim' and isinstance(rec['value'], (int, float)):
                        v = f'{rec["value"]:g}'.replace('.', ',')
                        if v not in numbers_in(f['text_vi']) and len(v) > 1:
                            warns.append({'code': 'W1', 'key': k, 'detail': f'{where}: {r} value {v} not in the fact text'})
                    if f['level'] == 'sourced' and rec['kind'] == 'photo' and not rec['brand'].startswith(('ZE', 'KM')):
                        warns.append({'code': 'W2', 'key': k, 'detail': f'{where}: {r} shows another brand ({rec["brand"][:40]})'})
            if f['level'] == 'sourced' and not any(x in PUBLIC_EVIDENCE for x in kinds):
                fail('P07', k, f'{where}: sourced needs a claim, catalogue figure or photo')
            if f['level'] == 'derived' and not f.get('refs'):
                fail('P08', k, f'{where}: derived needs a ref')
            if f['level'] == 'assumption' and not (f.get('reason_vi') and f.get('reason_ja')):
                fail('P09', k, f'{where}: assumption needs reason_vi and reason_ja')
            for fld in ('text_ja', 'reason_ja'):
                if fld == 'reason_ja' and not f.get('reason_vi'):
                    continue
                t, vi_t = f.get(fld) or '', f.get(fld.replace('_ja', '_vi')) or ''
                # a language-neutral VI text (a formula) may stay as it is
                neutral = t == vi_t and not has_vietnamese(vi_t)
                if not t or has_vietnamese(t) or not (KANA_KANJI.search(t) or neutral):
                    fail('P10', k, f'{where}: {fld} is missing or not Japanese: {t[:40]!r}')
            blob = json.dumps(f, ensure_ascii=False)
            for s in DENY_STRINGS:
                if s in blob:
                    fail('P13', k, f'{where}: contains {s!r}')
        if strict:
            covered = set(e.get('free_numbers') or [])
            for f in facts:
                covered |= numbers_in(f.get('text_vi', ''))
            missing = sorted(numbers_in(vi) - covered)
            if missing:
                fail('P11', k, f'numbers without a fact: {", ".join(missing)}')
            for f in facts:
                for r in f.get('refs') or []:
                    rec = resolve(r, reg)
                    if rec and rec['kind'] != 'claim' and not i18n_for(r, rec, i18n).get('ja_ok'):
                        fail('P14', k, f'{r}: no Japanese title/caption in web/prov/sources.i18n.json')
    return {'ok': not fails, 'failures': fails, 'warnings': warns}


def i18n_for(ref, rec, i18n):
    """sources.i18n.json entries of a ref: the pinned ref first, then its base id"""
    out = dict(i18n.get(ref.partition('|')[0], {}))
    out.update(i18n.get(ref, {}))
    need = {'doc': 'title_ja', 'figure': 'caption_ja', 'photo': 'shows_ja'}.get(rec['kind'])
    out['ja_ok'] = bool(need is None or out.get(need))
    return out


# ---------------------------------------------------------------- build (PLAN-PROV §2.3)
OUT = os.path.join(BUILD, 'prov', 'out')
IMG_SIZES = {'t': (480, 78), 'l': (1280, 82)}


def make_images(rec, img_dir):
    """thumbnail and large JPEG of a figure/photo; rebuilt only when the source is newer"""
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit('make_prov build needs Pillow (python3 -m pip install --user pillow), or use --no-images')
    src = os.path.join(WS, rec['file'])
    if not os.path.isfile(src):
        raise SystemExit(f'P12: image missing: {rec["file"]}')
    os.makedirs(img_dir, exist_ok=True)
    dims = {}
    for tag, (edge, q) in IMG_SIZES.items():
        dst = os.path.join(img_dir, f'{rec["id"]}.{tag}.jpg')
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            with Image.open(src) as im:
                im = im.convert('RGBA')
                bg = Image.new('RGB', im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[3])
                bg.thumbnail((edge, edge), Image.LANCZOS)
                bg.save(dst, 'JPEG', quality=q, optimize=True, progressive=True)
        with Image.open(dst) as im:
            dims[tag] = im.size
    return dims


def public_source(ref, reg, i18n, img_dir, images):
    rec = resolve(ref, reg)
    tr = i18n_for(ref, rec, i18n)
    tr.pop('ja_ok')
    out = {k: v for k, v in rec.items() if k not in ('file', 'topic', 'id', 'brand')}
    out.update(tr)
    if rec['kind'] in ('figure', 'photo'):
        out['thumb'] = f'/data/prov/img/{rec["id"]}.t.jpg'
        out['large'] = f'/data/prov/img/{rec["id"]}.l.jpg'
        if images:
            d = make_images(rec, img_dir)
            out['tw'], out['th'] = d['t']
            out['w'], out['h'] = d['l']
    return out


def build(devices, lines_dir, reg, i18n, strict, out_dir=OUT, images=True):
    rep = check(devices, lines_dir, reg, i18n, strict)
    if not rep['ok']:
        return rep
    entries, _ = load_entries(lines_dir)
    if os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith('.json'):
                os.remove(os.path.join(out_dir, f))
    os.makedirs(out_dir, exist_ok=True)
    img_dir = os.path.join(out_dir, 'img')
    by_dev, cache = {}, {}
    for ln in device_lines(devices):
        by_dev.setdefault(ln['device'], []).append(ln)
    for dev, lns in by_dev.items():
        lines, refs = [], []
        for ln in lns:
            _g, e = entries[line_key(ln['vi'])]
            on = e.get('status') in ('curated', 'verified') and e.get('facts')
            facts = []
            for f in (e['facts'] if on else []):
                facts.append({k: f[k] for k in ('level', 'text_vi', 'text_ja', 'refs', 'reason_vi', 'reason_ja') if f.get(k)})
                refs += [r for r in f.get('refs') or [] if r not in refs]
            lines.append({'kind': ln['kind'], 'index': ln['index'], 'vi': ln['vi'],
                          'level': weakest(e['facts']) if on else None, 'facts': facts})
        sources = {}
        for r in refs:
            if r not in cache:
                cache[r] = public_source(r, reg, i18n, img_dir, images)
            sources[r] = cache[r]
        doc = {'version': 1, 'device_id': dev, 'lines': lines, 'sources': sources}
        blob = json.dumps(doc, ensure_ascii=False, sort_keys=True)
        for s in DENY_STRINGS:
            if s in blob:
                rep['failures'].append({'code': 'P13', 'key': None, 'device': dev, 'detail': f'published data contains {s!r}'})
        if len(blob.encode('utf-8')) > DEVICE_MAX_BYTES:
            rep['failures'].append({'code': 'P15', 'key': None, 'device': dev, 'detail': f'{len(blob)} bytes'})
        with open(os.path.join(out_dir, f'{dev}.json'), 'w', encoding='utf-8') as f:
            f.write(blob)
    if images and os.path.isdir(img_dir):
        keep = {f'{s["thumb"].rsplit("/", 1)[1]}' for s in cache.values() if 'thumb' in s} | \
               {f'{s["large"].rsplit("/", 1)[1]}' for s in cache.values() if 'large' in s}
        for f in os.listdir(img_dir):
            if f not in keep:
                os.remove(os.path.join(img_dir, f))
    rep['ok'] = not rep['failures']
    rep['devices'] = len(by_dev)
    return rep


def coverage(devices, lines_dir):
    entries, _ = load_entries(lines_dir)
    cov = {}
    for k, (g, e) in entries.items():
        c = cov.setdefault(g, {'lines': 0, 'uses': 0, 'line_level': {}, 'facts': {}})
        c['lines'] += 1
        c['uses'] += len(e.get('used_by', []))
        on = e.get('status') != 'draft' and e.get('facts')
        lv = weakest(e['facts']) if on else 'unknown'
        c['line_level'][lv] = c['line_level'].get(lv, 0) + 1
        for f in (e['facts'] if on else []):
            c['facts'][f['level']] = c['facts'].get(f['level'], 0) + 1
        c.setdefault('status', {})
        c['status'][e.get('status', 'draft')] = c['status'].get(e.get('status', 'draft'), 0) + 1
    return cov


# ---------------------------------------------------------------- CLI
def write_json(path, obj, indent=None):
    path = os.path.abspath(path)
    if not (path + os.sep).startswith(BUILD + os.sep):
        raise SystemExit(f'refusing to write outside web/build/: {path}')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, sort_keys=True)


def cmd_registry(_a):
    reg = build_registry()
    write_json(os.path.join(BUILD, 'prov', 'registry.json'), reg, indent=0)
    kinds = {}
    for r in reg.values():
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    print('make_prov registry:', len(reg), 'refs', kinds)
    return reg


def cmd_selftest(a):
    reg = cmd_registry(a)
    bad = unresolved_tokens(reg)
    n = sum(len(tokens_of(p.get('source', ''))) for p in parts())
    print(f'make_prov selftest: {n} tokens in {len(parts())} sources | unresolved {len(bad)}')
    for b in bad:
        print('  UNRESOLVED', b)
    sys.exit(1 if bad else 0)


def cmd_seed(a):
    groups = seed(load_devices(a.devices), a.lines)
    n = sum(len(es) for es in groups.values())
    uses = sum(len(e['used_by']) for es in groups.values() for e in es.values())
    print(f'make_prov seed: {n} entries, {uses} uses, {len(groups)} group files -> {os.path.relpath(a.lines, WEB)}')


def report(rep, a):
    rep = dict(rep, strict=a.strict, lines=os.path.relpath(a.lines, WEB))
    write_json(os.path.join(BUILD, 'reports', 'prov_check.json'), rep, indent=1)
    cov = coverage(load_devices(a.devices), a.lines)
    write_json(os.path.join(BUILD, 'reports', 'prov_coverage.json'), cov, indent=1)
    codes = {}
    for f in rep['failures']:
        codes[f['code']] = codes.get(f['code'], 0) + 1
    tot = {}
    for c in cov.values():
        for lv, n in c['line_level'].items():
            tot[lv] = tot.get(lv, 0) + n
    print(f'make_prov {a.cmd}{" --strict" if a.strict else ""}: lines {tot} | failures {codes or 0} | warnings {len(rep["warnings"])}')
    for f in rep['failures'][:25]:
        print(f'  {f["code"]} {f["key"]} {f.get("device") or ""} {f["detail"]}')
    if len(rep['failures']) > 25:
        print(f'  ... {len(rep["failures"]) - 25} more in build/reports/prov_check.json')
    sys.exit(0 if rep['ok'] else 1)


def load_i18n():
    return load_json(os.path.join(WEB, 'prov', 'sources.i18n.json'))


def cmd_check(a):
    report(check(load_devices(a.devices), a.lines, build_registry(), load_i18n(), a.strict), a)


def cmd_build(a):
    reg = cmd_registry(a)
    rep = build(load_devices(a.devices), a.lines, reg, load_i18n(), a.strict, OUT, images=not a.no_images)
    if rep['ok']:
        imgs = os.listdir(os.path.join(OUT, 'img')) if os.path.isdir(os.path.join(OUT, 'img')) else []
        size = sum(os.path.getsize(os.path.join(OUT, 'img', f)) for f in imgs)
        print(f'make_prov build: {rep["devices"]} device files, {len(imgs)} images ({size / 1e6:.1f} MB) -> {os.path.relpath(OUT, WEB)}')
    report(rep, a)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('registry')
    sub.add_parser('selftest')
    s = sub.add_parser('seed')
    c = sub.add_parser('check')
    b = sub.add_parser('build')
    for p in (s, c, b):
        p.add_argument('--devices', default=DEVICES)
        p.add_argument('--lines', default=LINES)
    for p in (c, b):
        p.add_argument('--strict', action='store_true', help='every line verified, every number covered, Japanese titles (P03, P04, P11, P14)')
    b.add_argument('--no-images', action='store_true')
    a = ap.parse_args()
    {'registry': cmd_registry, 'selftest': cmd_selftest, 'seed': cmd_seed, 'check': cmd_check, 'build': cmd_build}[a.cmd](a)


if __name__ == '__main__':
    main()
