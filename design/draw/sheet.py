"""Drafting helpers: sheet frame, title block, projected views from geom.py, dimensions, balloons, tables."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle
from PIL import Image, ImageDraw

import geom
from geom import P, NUM, VIEWS, ROOT, scene

plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "lines.scale_dashes": False,
                     "hatch.linewidth": 0.4, "path.simplify": False})
PT = 72 / 25.4
SIZES = {"A0": (1189, 841), "A1": (841, 594)}
DASH = {"hidden": (0, (7, 3.5)), "center": (0, (22, 3.5, 3, 3.5)), "phantom": (0, (22, 3, 3, 3, 3, 3)),
        "solid": "-", "cut": (0, (22, 3.5, 3, 3.5))}
OUT = ROOT / "drawings"
N_SHEETS = 9
MIN_FS = 9.8  # DejaVu cap height 0.73 em -> 2.5 mm at print size (ISO 3098 h = 2.5)
REG = ROOT / "design" / "draw" / "balloon_index.json"
import os
VERBOSE = bool(os.environ.get("DRAW_VERBOSE"))
DATE = "2026-10-04"
PROJECT = "Máy đùn trục vít đôi ZE 155 A UT, L/D 34 – đường chảy nhựa và khuôn chữ T nằm ngang (dây chuyền tấm PET)"


def fmt(v):
    v = round(v)
    s = f"{abs(v):,}".replace(",", " ")
    return ("−" if v < 0 else "") + s


def short(t, width_mm, fs):
    cw = 0.56 * fs / PT
    n = max(3, int(width_mm / cw))
    return t if len(t) <= n else t[:n - 1] + "…"


class Sheet:
    def __init__(self, num, slug, title, size="A1", scale="1:20", subtitle=""):
        self.num, self.slug, self.title, self.size, self.scale = num, slug, title, size, scale
        self.W, self.H = SIZES[size]
        self.fig = plt.figure(figsize=(self.W / 25.4, self.H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, self.W)
        self.ax.set_ylim(0, self.H)
        self.ax.axis("off")
        self.subtitle = subtitle
        self.ballooned, self.mentioned = set(), set()
        self.frame()
        self.title_block()

    # ---------------------------------------------------------------- frame and title block
    def frame(self):
        ax = self.ax
        x0, y0, x1, y1 = 20, 12, self.W - 12, self.H - 12
        self.fx0, self.fy0, self.fx1, self.fy1 = x0, y0, x1, y1
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=0.7 * PT, ec="k"))
        nx = 8 if self.size == "A1" else 12
        ny = 6 if self.size == "A1" else 8
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            ax.plot([x, x], [y0, y0 - 8], lw=0.25 * PT, c="k")
            ax.plot([x, x], [y1, y1 + 8], lw=0.25 * PT, c="k")
            if i < nx:
                xm = x + (x1 - x0) / nx / 2
                ax.text(xm, y0 - 4.5, str(i + 1), ha="center", va="center", fontsize=MIN_FS)
                ax.text(xm, y1 + 4.5, str(i + 1), ha="center", va="center", fontsize=MIN_FS)
        for j in range(ny + 1):
            y = y0 + (y1 - y0) * j / ny
            ax.plot([x0, x0 - 8], [y, y], lw=0.25 * PT, c="k")
            ax.plot([x1, x1 + 8], [y, y], lw=0.25 * PT, c="k")
            if j < ny:
                ym = y + (y1 - y0) / ny / 2
                L = "ABCDEFGH"[ny - 1 - j]
                ax.text(x0 - 6, ym, L, ha="center", va="center", fontsize=MIN_FS)
                ax.text(x1 + 4.5, ym, L, ha="center", va="center", fontsize=MIN_FS)

    def title_block(self):
        ax = self.ax
        w, h = 250, 84
        x0, y0 = self.fx1 - w, self.fy0
        self.tb = (x0, y0, w, h)
        lw = 0.5 * PT
        ax.add_patch(Rectangle((x0, y0), w, h, fill=True, fc="white", ec="k", lw=0.7 * PT, zorder=20))
        rows = [y0 + h - 18, y0 + h - 40, y0 + 26, y0 + 13]
        for y in rows:
            ax.plot([x0, x0 + w], [y, y], c="k", lw=lw, zorder=21)
        T = lambda x, y, t, fs=MIN_FS, **k: ax.text(x, y, t, fontsize=max(fs, MIN_FS), zorder=22, **k)
        T(x0 + 2, y0 + h - 2.5, "Dự án (project)", va="top")
        T(x0 + 2, y0 + h - 8.5, "ZE 155 A UT, L/D 34 + đường chảy + khuôn chữ T (T-die)", 11, va="top", weight="bold")
        T(x0 + 2, y0 + h - 20.5, "Tên bản vẽ (sheet title)", va="top")
        T(x0 + 2, y0 + h - 26.5, self.title, 15, va="top", weight="bold")
        if self.subtitle:
            ax.text(x0 + w + 0, y0 + h + 15, "", fontsize=MIN_FS)
        cols = [x0, x0 + 46, x0 + 76, x0 + 118, x0 + 160, x0 + 250]
        for x in cols[1:-1]:
            ax.plot([x, x], [y0 + 26, y0 + h - 40], c="k", lw=lw, zorder=21)
        fields = [("Tỷ lệ (scale)", self.scale), ("Tờ (sheet)", f"{self.num}/{N_SHEETS}"), ("Ngày (date)", DATE),
                  ("Đơn vị (units)", "mm"), ("Số bản vẽ (drawing no.)", f"ZE155-TD-{self.num:02d}")]
        for (lab, val), xa, xb in zip(fields, cols[:-1], cols[1:]):
            T(xa + 1.5, y0 + h - 41.5, lab, va="top")
            T((xa + xb) / 2, y0 + 31.5, val, 11 if len(val) < 14 else MIN_FS, ha="center", va="center", weight="bold")
        T(x0 + 2, y0 + 19.5, "vẽ: Claude (giả định ghi chú G)", 10.5, va="center")
        ax.plot([x0 + 160, x0 + 160], [y0 + 13, y0 + 26], c="k", lw=lw, zorder=21)
        T(x0 + 162, y0 + 19.5, "góc thứ nhất (ISO E)", va="center")
        T(x0 + 2, y0 + 6.5, f"Dữ liệu: design/parts.json ({len(geom.ORDER)} chi tiết, {len(geom.CONN)} mối nối)", va="center")
        sx, sy = x0 + 236, y0 + 19.5
        ax.add_patch(Circle((sx - 6.5, sy), 4.2, fill=False, lw=0.35 * PT, zorder=22))
        ax.add_patch(Circle((sx - 6.5, sy), 2.1, fill=False, lw=0.35 * PT, zorder=22))
        ax.add_patch(Polygon([(sx - 1, sy - 4.2), (sx + 9, sy - 2.1), (sx + 9, sy + 2.1), (sx - 1, sy + 4.2)], closed=True,
                             fill=False, lw=0.35 * PT, zorder=22))
        ry = y0 + h
        ax.add_patch(Rectangle((x0, ry), w, 12, fc="white", ec="k", lw=0.5 * PT, zorder=20))
        ax.plot([x0 + 22, x0 + 22], [ry, ry + 12], c="k", lw=lw, zorder=21)
        ax.plot([x0 + 52, x0 + 52], [ry, ry + 12], c="k", lw=lw, zorder=21)
        T(x0 + 11, ry + 6, "Rev. B", ha="center", va="center", weight="bold")
        T(x0 + 37, ry + 6, DATE, ha="center", va="center")
        T(x0 + 54, ry + 6, "sửa theo review-01 (bản vẽ + dữ liệu)", va="center")
        if self.subtitle:
            ax.add_patch(Rectangle((x0, ry + 12), w, 14, fc="white", ec="k", lw=0.5 * PT, zorder=20))
            for j, ln in enumerate(wrap(self.subtitle, w - 4, MIN_FS)[:2]):
                T(x0 + 2, ry + 22 - j * 5.2, ln, va="center")

    def frame_check(self):
        """Report annotation lines that leave the drawing frame."""
        bad = 0
        for ln in self.ax.lines:
            if ln.get_zorder() < 20:
                continue
            xs, ys = ln.get_xdata(), ln.get_ydata()
            if any(x < self.fx0 - 0.5 or x > self.fx1 + 0.5 for x in xs) or any(y < self.fy0 - 0.5 or y > self.fy1 + 0.5 for y in ys):
                bad += 1
                if VERBOSE:
                    print("   out of frame line:", list(zip(xs, ys))[:3])
        for pa in self.ax.patches:
            if pa.get_zorder() < 40:
                continue
            ext = pa.get_extents().transformed(self.ax.transData.inverted())
            if ext.x0 < self.fx0 - 0.5 or ext.x1 > self.fx1 + 0.5 or ext.y0 < self.fy0 - 0.5 or ext.y1 > self.fy1 + 0.5:
                bad += 1
                if VERBOSE:
                    print("   out of frame patch:", ext)
        return bad

    def labels_column(self, items, x, y_top, step=6.2, fs=MIN_FS, ha="left"):
        """Labels stacked in one column, ordered like their targets so leaders do not cross.
        items: (target, text) or (target, text, part_id)."""
        items = sorted(items, key=lambda it: -it[0][1])
        for i, it in enumerate(items):
            self.label(it[0], (x, y_top - i * step), it[1], fs, ha=ha, pid=it[2] if len(it) > 2 else None)

    def text_overlaps(self, verbose=False):
        """Pairs of overlapping text boxes (drawn size), used to hunt label collisions."""
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        boxes = []
        for t in self.ax.texts:
            if not t.get_text().strip() or not t.get_visible():
                continue
            bb = t.get_window_extent(r)
            boxes.append((bb.x0 + 1, bb.y0 + 1, bb.x1 - 1, bb.y1 - 1, t.get_text()[:40]))
        boxes.sort()
        out = []
        for i in range(len(boxes)):
            a = boxes[i]
            for j in range(i + 1, len(boxes)):
                b = boxes[j]
                if b[0] > a[2]:
                    break
                if b[1] < a[3] and b[3] > a[1] and b[0] < a[2]:
                    out.append((a[4], b[4]))
        if verbose:
            for p in out:
                print("   overlap:", p)
        return out

    def save(self):
        n_out = self.frame_check()
        if n_out:
            print(f"  warning: {n_out} annotation items leave the frame on sheet {self.num}")
        ov = self.text_overlaps(verbose=VERBOSE)
        print(f"  sheet {self.num}: {len(ov)} overlapping text pairs, frame check {n_out}")
        name = f"sheet-{self.num:02d}-{self.slug}"
        self.fig.savefig(OUT / f"{name}.svg")
        dpi = min(200, 7900 / (self.W / 25.4))
        import json as _json
        reg = _json.loads(REG.read_text()) if REG.exists() else {}
        reg[str(self.num)] = sorted(self.ballooned | self.mentioned)
        REG.write_text(_json.dumps(reg, indent=0))
        self.fig.savefig(OUT / f"{name}.png", dpi=dpi)
        plt.close(self.fig)
        return name, dpi

    # ---------------------------------------------------------------- annotation primitives
    def text(self, x, y, s, fs=MIN_FS, **k):
        k.setdefault("zorder", 30)
        return self.ax.text(x, y, s, fontsize=max(fs, MIN_FS), **k)

    def line(self, pts, lw=0.25, ls="solid", c="k", z=25):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, c=c, lw=lw * PT, ls=DASH.get(ls, ls), zorder=z, solid_capstyle="butt")

    def arrow(self, tip, frm, size=3.2, c="k", z=26):
        dx, dy = tip[0] - frm[0], tip[1] - frm[1]
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        b = (tip[0] - ux * size, tip[1] - uy * size)
        w = size * 0.18
        self.ax.add_patch(Polygon([tip, (b[0] - uy * w, b[1] + ux * w), (b[0] + uy * w, b[1] - ux * w)], closed=True,
                                  fc=c, ec=c, lw=0.1, zorder=z))

    def dim(self, p1, p2, pos, orient="h", text=None, value=None, fs=MIN_FS, ext=True, gap=1.0, tpos=None):
        """Linear dimension between sheet points p1, p2. orient 'h': dim line at y=pos; 'v': at x=pos."""
        if orient == "h":
            a, b = (p1[0], pos), (p2[0], pos)
            if ext:
                for p in (p1, p2):
                    s = 1 if pos > p[1] else -1
                    self.line([(p[0], p[1] + s * gap), (p[0], pos + s * 1.5)], lw=0.18)
        else:
            a, b = (pos, p1[1]), (pos, p2[1])
            if ext:
                for p in (p1, p2):
                    s = 1 if pos > p[0] else -1
                    self.line([(p[0] + s * gap, p[1]), (pos + s * 1.5, p[1])], lw=0.18)
        self.line([a, b], lw=0.18)
        L = math.dist(a, b)
        if L > 6.5:
            self.arrow(a, b)
            self.arrow(b, a)
        else:
            for t, f in ((a, b), (b, a)):
                d = ((t[0] - f[0]) / (L or 1), (t[1] - f[1]) / (L or 1))
                self.line([t, (t[0] + d[0] * 4, t[1] + d[1] * 4)], lw=0.18)
                self.arrow(t, (t[0] + d[0] * 4, t[1] + d[1] * 4))
        s = text if text is not None else fmt(value)
        m = tpos or ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if orient == "h":
            self.text(m[0], m[1] + 0.8, s, fs, ha="center", va="bottom", zorder=43, bbox=dict(fc="white", ec="none", pad=0.15))
        else:
            self.text(m[0] - 0.8, m[1], s, fs, ha="right" if tpos else "center", va="bottom" if not tpos else "center",
                      rotation=0 if tpos else 90, zorder=43, bbox=dict(fc="white", ec="none", pad=0.15),
                      **({} if tpos else {"rotation_mode": "anchor"}))

    def balloon(self, at, pos, label, r=5.2, fs=10.5, dot=True, pid=None):
        if pid:
            self.ballooned.add(pid)
        dx, dy = at[0] - pos[0], at[1] - pos[1]
        L = math.hypot(dx, dy) or 1
        st = (pos[0] + dx / L * r, pos[1] + dy / L * r)
        self.line([st, at], lw=0.18, z=40)
        if dot:
            self.ax.add_patch(Circle(at, 0.55, fc="k", ec="k", zorder=41))
        self.ax.add_patch(Circle(pos, r, fc="white", ec="k", lw=0.3 * PT, zorder=41))
        self.text(pos[0], pos[1], str(label), fs if len(str(label)) < 3 else fs - 0.6, ha="center", va="center", zorder=42)

    def label(self, at, pos, s, fs=MIN_FS, ha=None, dot=True, pid=None):
        if pid:
            self.mentioned.add(pid)
        self.line([at, pos], lw=0.18, z=40)
        if dot:
            self.ax.add_patch(Circle(at, 0.5, fc="k", ec="k", zorder=41))
        ha = ha or ("left" if pos[0] >= at[0] else "right")
        self.line([pos, (pos[0] + (3 if ha == "left" else -3), pos[1])], lw=0.18, z=40)
        self.text(pos[0] + (3.5 if ha == "left" else -3.5), pos[1], s, fs, ha=ha, va="center",
                  bbox=dict(fc="white", ec="none", pad=0.4), zorder=42)

    def heading(self, x, y, s, scale=None, fs=14, sub=None):
        t = s + (f"   {scale}" if scale else "")
        self.text(x, y, t, fs, ha="center", va="bottom", weight="bold")
        tw = len(t) * 0.55 * fs / PT
        self.line([(x - tw / 2, y - 1.0), (x + tw / 2, y - 1.0)], lw=0.35)
        if sub:
            self.text(x, y - 2.5, sub, MIN_FS, ha="center", va="top", style="italic")

    def table(self, x, ytop, cols, rows, rowh=5.4, fs=MIN_FS, hfs=MIN_FS, title=None, zebra=False):
        fs, hfs = max(fs, MIN_FS), max(hfs, MIN_FS)
        ax = self.ax
        wsum = sum(c[1] for c in cols)
        y = ytop
        if title:
            self.text(x, y + 1.5, title, 11, va="bottom", weight="bold")
        ax.add_patch(Rectangle((x, y - rowh * 1.25), wsum, rowh * 1.25, fc="#e6e6e6", ec="k", lw=0.35 * PT, zorder=24))
        cx = x
        for name, wdt, al in cols:
            self.text(cx + (1.0 if al == "l" else wdt / 2), y - rowh * 0.625, name, hfs, ha="left" if al == "l" else "center",
                      va="center", weight="bold")
            cx += wdt
        y -= rowh * 1.25
        for i, r in enumerate(rows):
            if zebra and i % 2:
                ax.add_patch(Rectangle((x, y - rowh), wsum, rowh, fc="#f4f4f4", ec="none", zorder=23))
            cx = x
            for (name, wdt, al), val in zip(cols, r):
                s = short(str(val), wdt - 1.5, fs)
                self.text(cx + (0.8 if al == "l" else wdt / 2), y - rowh / 2, s, fs, ha="left" if al == "l" else "center", va="center")
                cx += wdt
            y -= rowh
            ax.plot([x, x + wsum], [y, y], c="k", lw=0.12 * PT, zorder=24)
        ax.add_patch(Rectangle((x, y), wsum, ytop - y, fill=False, ec="k", lw=0.35 * PT, zorder=24))
        cx = x
        for name, wdt, al in cols[:-1]:
            cx += wdt
            ax.plot([cx, cx], [y, ytop], c="k", lw=0.12 * PT, zorder=24)
        return y

    def notes(self, x, ytop, title, items, fs=MIN_FS, width=None, lh=1.5):
        fs = max(fs, MIN_FS)
        self.text(x, ytop, title, 11, va="top", weight="bold")
        y = ytop - 11 / PT * 1.8
        for it in items:
            lines = wrap(it, width, fs) if width else [it]
            for j, ln in enumerate(lines):
                self.text(x + (0 if j == 0 else 3), y, ln, fs, va="top")
                y -= fs / PT * lh
        return y


def wrap(s, width_mm, fs):
    cw = 0.53 * fs / PT
    n = max(10, int(width_mm / cw))
    out, cur = [], ""
    for w in s.split(" "):
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


class VP:
    """A projected view placed on a sheet: world (u, w) -> sheet mm."""

    def __init__(self, sh, view, k, ox, oy, uc, wc, clip=None):
        self.sh, self.v, self.k = sh, (VIEWS[view] if isinstance(view, str) else view), k
        self.ox, self.oy, self.uc, self.wc = ox, oy, uc, wc
        self.clip = clip  # world (u0, u1, w0, w1)
        self.items = []

    def xy(self, u, w):
        return self.ox + (u - self.uc) / self.k, self.oy + (w - self.wc) / self.k

    def P(self, p3):
        return self.xy(*self.v.uv(p3))

    def box(self):
        u0, u1, w0, w1 = self.clip
        (x0, y0), (x1, y1) = self.xy(u0, w0), self.xy(u1, w1)
        return min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)

    def draw(self, ids, phantom=(), hidden_show=True, thick=0.35, thin=0.18, exclude=("ctx_floor",), extra_hidden=(),
             cut_parts=(), floor=True, ghost=None, z0=5.0):
        """ghost: edge colour -> every part drawn as a light outline with white fill (context under routing)."""
        ax = self.sh.ax
        items = scene(self.v, ids, exclude=exclude)
        self.items = items
        cp = None
        if self.clip:
            x0, x1, y0, y1 = self.box()
            cp = Rectangle((x0, y0), x1 - x0, y1 - y0, transform=ax.transData)
        later = []
        z = z0
        for it in items:
            grp = P[it["part"]]["group"]
            if ghost:
                if it["hidden"] or it.get("noline") and not it["fill"]:
                    continue
                z += 1e-4
                if it.get("noline"):
                    self._patch(it, "white" if it["fill"] else "none", "none", 0, "-", z, cp)
                else:
                    self._patch(it, "white" if it["fill"] and grp != "context" else "none", ghost, thin * 0.8 * PT,
                                DASH["phantom"] if grp == "context" else "-", z, cp)
                continue
            if grp == "context" or it["part"] in phantom:
                later.append(("ph", it))
                continue
            if it["hidden"]:
                if hidden_show:
                    later.append(("hid", it))
                continue
            sh = it["shade"]
            fc = {"dark": "#8c8c8c", "mid": "#cfcfcf", "light": "#f2f2f2"}.get(sh, "white") if it["fill"] else "none"
            lw = (thick if it["lw"] == "thick" else thin) * PT
            z += 1e-4
            if it.get("noline"):
                if fc != "none":
                    self._patch(it, fc, "none", 0, "-", z, cp)
            else:
                self._patch(it, fc, "k", lw, "-", z, cp)
        for kind, it in later:
            z += 1e-4
            if it.get("noline"):
                continue
            if kind == "ph":
                self._patch(it, "none", "#555555", thin * PT, DASH["phantom"], z + 2, cp)
            else:
                self._patch(it, "none", "k", thin * PT, DASH["hidden"], z + 1, cp)
        if floor and self.v.U[2] > 0.5 and self.clip:
            u0, u1, w0, w1 = self.clip
            a, b = self.xy(u0, 0), self.xy(u1, 0)
            self.sh.line([a, b], lw=0.35, z=30)
            xs = np.arange(min(a[0], b[0]) + 2, max(a[0], b[0]) - 2, 4)
            for x in xs:
                self.sh.line([(x, a[1]), (x - 2, a[1] - 2)], lw=0.13, z=30)

    def breaks(self, *edges):
        """Break lines (ISO 128 zig-zag) on the clipped edges of the view window: 'left', 'right', 'top', 'bottom'."""
        import drafting
        x0, x1, y0, y1 = self.box()
        seg = {"left": ((x0, y0 + 3), (x0, y1 - 3)), "right": ((x1, y0 + 3), (x1, y1 - 3)),
               "top": ((x0 + 3, y1), (x1 - 3, y1)), "bottom": ((x0 + 3, y0), (x1 - 3, y0))}
        for e in edges:
            drafting.break_line(self.sh, *seg[e])

    def _patch(self, it, fc, ec, lw, ls, z, cp):
        ax = self.sh.ax
        if it["type"] == "poly":
            pts = [self.xy(a, b) for a, b in it["geo"]]
            if len(pts) < 3:
                art, = ax.plot(*zip(*pts), c=ec, lw=lw, ls=ls, zorder=z)
            else:
                art = Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, joinstyle="miter")
                ax.add_patch(art)
        elif it["type"] == "circle":
            (a, b), r = it["geo"]
            art = Circle(self.xy(a, b), r / self.k, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z)
            ax.add_patch(art)
        else:
            pts = [self.xy(a, b) for a, b in it["geo"]]
            art, = ax.plot(*zip(*pts), c=ec, lw=lw, ls=ls if ls != "-" else "-", zorder=z)
        if cp is not None:
            art.set_clip_path(cp)

    # --------------------------------------------------------------- visibility for balloons
    def idbuffer(self, res=2.0):
        x0, x1, y0, y1 = self.box()
        W, H = int((x1 - x0) * res) + 1, int((y1 - y0) * res) + 1
        img = Image.new("I", (W, H), 0)
        dr = ImageDraw.Draw(img)
        idx = {}
        for it in self.items:
            if not it["fill"] or not it["sil"] or it["hidden"] or P[it["part"]]["group"] == "context":
                continue
            n = idx.setdefault(it["part"], len(idx) + 1)

            def px(a, b):
                x, y = self.xy(a, b)
                return (x - x0) * res, (y1 - y) * res
            if it["type"] == "poly" and len(it["geo"]) >= 3:
                dr.polygon([px(a, b) for a, b in it["geo"]], fill=n)
            elif it["type"] == "circle":
                (a, b), r = it["geo"]
                cx, cy = px(a, b)
                rp = r / self.k * res
                dr.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=n)
        self._ib = (np.asarray(img), idx, x0, y1, res)
        return self._ib

    def target(self, pid, prefer=None):
        """A visible point of part pid (sheet mm), or bbox centre if not visible."""
        if not hasattr(self, "_ib"):
            self.idbuffer()
        arr, idx, x0, y1, res = self._ib
        n = idx.get(pid)
        if n:
            ys, xs = np.nonzero(arr == n)
            if len(xs):
                if prefer is not None:
                    px_, py_ = (prefer[0] - x0) * res, (y1 - prefer[1]) * res
                    i = np.argmin((xs - px_) ** 2 + (ys - py_) ** 2)
                else:
                    cx, cy = xs.mean(), ys.mean()
                    # point well inside: maximise distance to the region border approximately
                    d = (xs - cx) ** 2 + (ys - cy) ** 2
                    i = np.argmin(d)
                return x0 + xs[i] / res, y1 - ys[i] / res
        b = P[pid]["bbox_mm"]
        pt = self.P(((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2))
        if self.clip:
            x0, x1, y0, y1 = self.box()
            if not (x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1):
                return None  # part not in this view window: no leader
        return pt

    def visible_area(self, pid):
        if not hasattr(self, "_ib"):
            self.idbuffer()
        arr, idx, *_ = self._ib
        n = idx.get(pid)
        return int((arr == n).sum()) if n else 0

    def balloons(self, ids, sides=("top", "bottom"), offset=10, spacing=11.5, r=5.2, box=None, rows=1):
        ids = [q for q in ids if q in P]
        spacing = max(spacing, 2 * r + 1.2)
        bx0, bx1, by0, by1 = box or self.box()
        tg = {pid: self.target(pid) for pid in ids}
        tg = {k: v for k, v in tg.items() if v is not None}
        groups = {s: [] for s in sides}
        for pid, (x, y) in tg.items():
            dist = {"top": by1 - y, "bottom": y - by0, "left": x - bx0, "right": bx1 - x}
            s = min(sides, key=lambda q: dist[q])
            groups[s].append(pid)
        for s, pids in groups.items():
            horiz = s in ("top", "bottom")
            pids.sort(key=lambda q: tg[q][0] if horiz else tg[q][1])
            pos = [tg[q][0] if horiz else tg[q][1] for q in pids]
            lo, hi = (bx0, bx1) if horiz else (by0, by1)
            for it in range(60):
                for i in range(1, len(pos)):
                    if pos[i] - pos[i - 1] < spacing:
                        m = (pos[i] + pos[i - 1]) / 2
                        pos[i - 1], pos[i] = m - spacing / 2, m + spacing / 2
                pos = [min(max(p, lo + r), hi - r) for p in pos]
            for j, (pid, p) in enumerate(zip(pids, pos)):
                off = offset + (j % rows) * (2.3 * r)
                if s == "top":
                    xy = (p, by1 + off)
                elif s == "bottom":
                    xy = (p, by0 - off)
                elif s == "left":
                    xy = (bx0 - off, p)
                else:
                    xy = (bx1 + off, p)
                self.sh.balloon(tg[pid], xy, NUM[pid], r=r, pid=pid)

    def cline(self, p3a, p3b, lw=0.18):
        self.sh.line([self.P(p3a), self.P(p3b)], lw=lw, ls="center", z=35)

    def dimw(self, p3a, p3b, pos_world, orient="h", text=None, value=None, **k):
        """Dimension between two world points; pos_world = world coordinate (w for 'h', u for 'v') of the dim line."""
        a, b = self.P(p3a), self.P(p3b)
        ua, wa = self.v.uv(p3a)
        ub, wb = self.v.uv(p3b)
        if orient == "h":
            pos = self.xy(0, pos_world)[1]
            val = abs(ub - ua)
        else:
            pos = self.xy(pos_world, 0)[0]
            val = abs(wb - wa)
        self.sh.dim(a, b, pos, orient, text=text, value=val if value is None else value, **k)


def sheet_parts_list(sh, x, ytop, extra=(), title="Danh mục chi tiết trên tờ (parts list)", **k):
    ids = sorted(set(sh.ballooned) | set(sh.mentioned) | set(q for q in extra if q in P), key=lambda q: NUM[q])
    return sh.table(x, ytop, BOM_COLS, bom_rows(ids), title=title, **k)


def bom_rows(ids):
    rows = []
    for pid in ids:
        p = P[pid]
        n = p.get("count", 1) or 1
        g = "G" if "giả định" in p["source"] else ""
        rows.append([NUM[pid], pid, p["name_vi"], n, f"{p['material']} {p['colour_hex']}", g])
    return rows


BOM_COLS = [("Số", 11, "c"), ("Mã (id)", 62, "l"), ("Tên chi tiết", 108, "l"), ("SL", 10, "c"), ("Vật liệu / màu", 50, "l"), ("G", 7, "c")]
