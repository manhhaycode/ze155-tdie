"""Check the label pacing rules of anim/shots.json (read only) and the font coverage.

    uv run -q --with pillow --with numpy python anim/post/check_timing.py [--out anim/post/timing_report.md]

Rules (design-anim.md §3 "Nhịp đọc", shots.json meta.label_rule):
  R1  each label on screen >= max(3 s, 0.4 s/word) = max(75, 10 x words) frames
  R2  at most 4 labels at once (S15: at most 2)
  R3  the last label of a shot holds >= 3 s
  R4  labels lie inside their shot; shots tile frames 1..5275 without gaps
  R5  every shot whose visible text has '*' has the footer "* = giả định ..."
Convention: a label is on screen on frame_in..frame_out inclusive (frame_out - frame_in + 1 frames),
with an 8-frame fade at each end. R2 is reported twice: counting every partly visible frame (strict),
and counting only fully opaque frames (a fade-out overlapping the next fade-in is a crossfade).
Exit code 1 if any rule fails under the main convention (R1 inclusive, R2 opaque).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FADE, POST, label_min_frames, load_shots, missing_glyphs, words  # noqa: E402


def hud_strings():
    """Every fixed string overlay.py draws besides shots.json text (kept in sync by import)."""
    try:
        import overlay
        return overlay.all_fixed_strings()
    except Exception as e:  # pragma: no cover
        return [f'(overlay strings unavailable: {e})']


def collect_text(shot):
    t = [shot['title_vi'], shot.get('speed_badge_vi', '')] + [l['text'] for l in shot['labels']]
    hud = shot.get('hud', {})
    t += [hud.get('title', '')] + list(hud.get('values', [])) + list(hud.get('block_diagram', []))
    t += [hud.get('footer', ''), hud.get('gauge', '')]
    return t


def check(data):
    shots = data['shots']
    fails, notes, rows = [], [], []
    # R4 tiling
    expect = data['meta']['frame_start']
    for s in shots:
        a, b = s['frames']
        if a != expect:
            fails.append(f"R4 {s['id']}: starts at {a}, expected {expect}")
        expect = b + 1
        if abs((b - a + 1) / 25 - s['duration_s']) > 1e-6:
            fails.append(f"R4 {s['id']}: duration_s {s['duration_s']} != {(b - a + 1) / 25}")
    if expect - 1 != data['meta']['frame_end']:
        fails.append(f"R4 last frame {expect - 1} != meta.frame_end {data['meta']['frame_end']}")

    for s in shots:
        a, b = s['frames']
        L = s['labels']
        cap = 2 if s['id'] == 'S15' else 4
        for i, l in enumerate(L):
            need = label_min_frames(l['text'])
            dur_inc = l['frame_out'] - l['frame_in'] + 1
            dur_exc = l['frame_out'] - l['frame_in']
            opaque = dur_inc - 2 * (FADE - 1)
            status = 'ok'
            if dur_inc < need:
                status = 'FAIL'
                fails.append(f"R1 {s['id']} L{i}: {dur_inc} frames < {need} ({words(l['text'])} words) – {l['text']}")
            elif dur_exc < need:
                status = 'ok (0-frame margin)'
                notes.append(f"R1 {s['id']} L{i}: exactly {need} frames only when frame_out is counted "
                             f"({dur_exc} exclusive) – {l['text']}")
            if l.get('min_frames') not in (None, need):
                notes.append(f"{s['id']} L{i}: min_frames {l['min_frames']} != rule {need}")
            if l['frame_in'] < a or l['frame_out'] > b:
                fails.append(f"R4 {s['id']} L{i}: frames {l['frame_in']}–{l['frame_out']} outside shot {a}–{b}")
            rows.append((s['id'], i, l['frame_in'], l['frame_out'], dur_inc, need, opaque, status, l['text']))
        if L:
            last = max(L, key=lambda l: l['frame_in'])
            if last['frame_out'] - last['frame_in'] + 1 < 75:
                fails.append(f"R3 {s['id']}: last label holds < 3 s")
        strict, opq = [], []
        for f in range(a, b + 1):
            n = sum(1 for l in L if l['frame_in'] <= f <= l['frame_out'])
            n2 = sum(1 for l in L if l['frame_in'] + FADE - 1 <= f <= l['frame_out'] - FADE + 1)
            if n > cap:
                strict.append((f, n))
            if n2 > cap:
                opq.append((f, n2))
        if opq:
            fails.append(f"R2 {s['id']}: {len(opq)} frames with > {cap} fully opaque labels, first {opq[0]}")
        if strict:
            spans, start, prev = [], strict[0][0], strict[0][0]
            for f, _ in strict[1:]:
                if f != prev + 1:
                    spans.append((start, prev))
                    start = f
                prev = f
            spans.append((start, prev))
            notes.append(f"R2 {s['id']} (cap {cap}): {max(n for _, n in strict)} labels partly visible during "
                         f"crossfades {', '.join(f'{x}–{y}' for x, y in spans)} ({len(strict)} frames); "
                         f"never more than {cap} fully opaque")
        # R5 footer
        texts = collect_text(s)
        has_star = any('*' in t for t in texts if t and t != s['hud'].get('footer'))
        has_footer = bool(s.get('hud', {}).get('footer'))
        if has_star and not has_footer:
            fails.append(f"R5 {s['id']}: '*' on screen but no footer")
        if has_footer and not has_star:
            notes.append(f"R5 {s['id']}: footer shown although no '*' on screen")
    # fonts
    alltext = ' '.join(t for s in shots for t in collect_text(s)) + ' ' + ' '.join(hud_strings())
    for bold in (False, True):
        miss = missing_glyphs(alltext, bold)
        if miss:
            fails.append(f"FONT ({'bold' if bold else 'regular'}) lacks glyphs: {''.join(miss)}")
    return fails, notes, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shots', default=None)
    ap.add_argument('--out', default=os.path.join(POST, 'timing_report.md'))
    a = ap.parse_args()
    data = load_shots(a.shots) if a.shots else load_shots()
    fails, notes, rows = check(data)
    md = ['# Label timing check (generated by check_timing.py; do not edit)', '',
          f'Result: **{"FAIL" if fails else "PASS"}** – {len(fails)} failures, {len(notes)} notes.', '',
          'Convention: on screen frame_in..frame_out inclusive, 8-frame fades; R2 counts fully opaque labels.', '']
    md += ['## Failures', ''] + ([f'- {x}' for x in fails] or ['- none']) + ['']
    md += ['## Notes', ''] + ([f'- {x}' for x in notes] or ['- none']) + ['']
    md += ['## All labels', '', '| shot | # | in | out | frames | need | opaque | status | text |', '|---|---|---|---|---|---|---|---|---|']
    md += [f'| {r[0]} | L{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |' for r in rows]
    with open(a.out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    print(f'{"FAIL" if fails else "PASS"}: {len(fails)} failures, {len(notes)} notes -> {a.out}')
    for x in fails:
        print('  FAIL', x)
    for x in notes:
        print('  note', x)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
