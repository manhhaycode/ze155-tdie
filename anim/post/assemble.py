"""Assemble the ZE 155 animation into an MP4 (H.264, CRF 18, 25 fps) with the ffmpeg binary of imageio-ffmpeg.

    uv run -q --with pillow --with numpy --with imageio-ffmpeg python anim/post/assemble.py [options]

Sources
  --src final    (default) anim/render/final/####.png, written by overlay.py --mode final
  --src overlay  anim/render/frames/####.png + anim/render/overlay/####.png; ffmpeg composites the RGBA
                 overlay over each frame (straight alpha, RGB), so no composited PNGs are stored
Output  anim/render/ze155_anim.mp4 (full) or anim/render/preview.mp4 (--preview), or --out.

--preview: frame subset (--range) at 960x540, CRF 23, preset veryfast. Full mode refuses gaps in the
frame sequence unless --allow-gaps (a missing frame then repeats the previous one, and is reported).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FPS, RENDER, load_shots, parse_ranges  # noqa: E402


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def build_sequence(frames, dirs, policy):
    """Frames to encode. A frame needs a PNG in every dir. policy: error | repeat (previous frame) | drop."""
    ok = {f: all(os.path.exists(os.path.join(d, f'{f:04d}.png')) for d in dirs) for f in frames}
    missing = [f for f in frames if not ok[f]]
    if missing and policy == 'error':
        sys.exit(f'{len(missing)} frames missing ({missing[0]}…{missing[-1]}); render them or pass --allow-gaps')
    seq, last = [], None
    for f in frames:
        if ok[f]:
            seq.append(f)
            last = f
        elif policy == 'repeat' and last is not None:
            seq.append(last)
    return seq, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', choices=('final', 'overlay'), default='final')
    ap.add_argument('--final', default=os.path.join(RENDER, 'final'))
    ap.add_argument('--frames', default=os.path.join(RENDER, 'frames'))
    ap.add_argument('--overlay', default=os.path.join(RENDER, 'overlay'))
    ap.add_argument('--range', default=None, help="frames, e.g. '901-1350,4400-4500' (default all 1..5275)")
    ap.add_argument('--preview', action='store_true', help='960x540, CRF 23, veryfast')
    ap.add_argument('--size', default=None, help='output WxH, e.g. 1280x720 (default 1920x1080, preview 960x540)')
    ap.add_argument('--crf', type=int, default=None)
    ap.add_argument('--preset', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--allow-gaps', action='store_true')
    a = ap.parse_args()

    meta = load_shots()['meta']
    frames = parse_ranges(a.range) if a.range else list(range(meta['frame_start'], meta['frame_end'] + 1))
    size = a.size or ('960x540' if a.preview else '1920x1080')
    w, h = (int(v) for v in size.lower().split('x'))
    crf = a.crf if a.crf is not None else (23 if a.preview else 18)
    preset = a.preset or ('veryfast' if a.preview else 'slow')
    out = a.out or os.path.join(RENDER, 'preview.mp4' if a.preview else 'ze155_anim.mp4')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    dirs = [a.final] if a.src == 'final' else [a.frames, a.overlay]
    policy = 'drop' if a.preview else 'repeat' if a.allow_gaps else 'error'
    seq, missing = build_sequence(frames, dirs, policy)
    if not seq:
        sys.exit('no frames found in ' + ', '.join(dirs))
    tmp = tempfile.mkdtemp(prefix='.assemble_', dir=os.path.dirname(os.path.abspath(out)))
    try:
        for k, f in enumerate(seq):     # gap-free numbered symlinks, so any subset or order can be encoded
            for d, pre in zip(dirs, 'ab'):
                os.symlink(os.path.abspath(os.path.join(d, f'{f:04d}.png')), os.path.join(tmp, f'{pre}_{k:06d}.png'))
        n = len(seq)
        cmd = [ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(FPS),
               '-i', os.path.join(tmp, 'a_%06d.png')]
        if a.src == 'overlay':
            cmd += ['-framerate', str(FPS), '-i', os.path.join(tmp, 'b_%06d.png'),
                    '-filter_complex',
                    f'[0:v]scale={w}:{h}:flags=lanczos,format=gbrp[b];[1:v]scale={w}:{h}:flags=lanczos,format=gbrap[o];'
                    f'[b][o]overlay=format=gbrp:shortest=1,format=yuv420p[v]', '-map', '[v]']
        else:
            cmd += ['-vf', f'scale={w}:{h}:flags=lanczos,format=yuv420p']
        cmd += ['-c:v', 'libx264', '-crf', str(crf), '-preset', preset, '-pix_fmt', 'yuv420p',
                '-r', str(FPS), '-movflags', '+faststart', out]
        print(f'{n} frames ({frames[0]}–{frames[-1]}), {w}x{h}, CRF {crf}, {preset}, src {a.src} -> {out}')
        if missing:
            print(f'  {len(missing)} missing frames ' + ('dropped (preview)' if policy == 'drop' else 'repeat the previous frame')
                  + f': {missing[:8]}{"…" if len(missing) > 8 else ""}')
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    import imageio_ffmpeg
    nf, secs = imageio_ffmpeg.count_frames_and_secs(out)
    print(f'ok: {out}  {nf} frames, {secs:.2f} s, {os.path.getsize(out) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
