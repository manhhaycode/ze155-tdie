#!/usr/bin/env python3
"""Sheet 09 – full bill of materials (A0): every part in parts.json order, with the sheets on which it is ballooned or
named (read from balloon_index.json, which sheets 01-08 write when they are saved). Run after sheets 01-08."""
import json

from geom import ORDER, P, NUM
from sheet import Sheet, REG

FS = 12.0      # cap height 3.1 mm at print size
ROWH = 6.8
COLS = [("Số", 13, "c"), ("Mã (id)", 70, "l"), ("Tên chi tiết", 222, "l"), ("SL", 12, "c"), ("Vật liệu / màu", 166, "l"),
        ("Tờ (sheets)", 56, "l"), ("G", 9, "c")]


def main():
    reg = json.loads(REG.read_text()) if REG.exists() else {}
    where = {}
    for s, ids in reg.items():
        if s in ("9",):
            continue
        for pid in ids:
            where.setdefault(pid, set()).add(int(s))
    sh = Sheet(9, "bom", "Danh mục chi tiết (bill of materials)", size="A0", scale="—",
               subtitle=f"Đủ {len(ORDER)} chi tiết theo thứ tự parts.json; cột Tờ = các tờ có bóng số hoặc chú thích của chi tiết")
    rows = []
    for pid in ORDER:
        p = P[pid]
        n = p.get("count", 1) or 1
        g = "G" if "giả định" in p["source"] else ""
        tw = ", ".join(f"{s:02d}" for s in sorted(where.get(pid, ()))) or "–"
        rows.append([NUM[pid], pid, p["name_vi"], n, f"{p['material']} {p['colour_hex']}", tw, g])
    half = (len(rows) + 1) // 2
    w = sum(c[1] for c in COLS)
    x0 = 26
    for j, chunk in enumerate((rows[:half], rows[half:])):
        sh.table(x0 + j * (w + 10), 812, COLS, chunk, rowh=ROWH, fs=FS, hfs=FS, zebra=True,
                 title="Danh mục chi tiết (bill of materials), số = số bóng dùng chung mọi tờ" if j == 0 else None)
    missing = [NUM[q] for q in ORDER if q not in where]
    sh.notes(x0 + w + 10, 812 - ROWH * 1.25 - ROWH * (len(rows) - half) - 8, "Ghi chú", [
        "1. Số bóng = vị trí chi tiết trong parts.json; mọi tờ dùng chung số này. G = kích thước hoặc vị trí giả định (design.md).",
        "2. Cột Tờ sinh tự động từ bóng số và chú thích thực có trên các tờ 01–08 (design/draw/balloon_index.json).",
        f"3. Chi tiết chưa có trên tờ nào: {len(missing)}" + (f" (số {', '.join(map(str, missing))})." if missing else "."),
    ], fs=FS, width=w - 260)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
