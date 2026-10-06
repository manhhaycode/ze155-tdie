# Nguồn cho từng dòng giải thích (PROV): kế hoạch thực hiện

> **Cho agent thực hiện:** dùng superpowers:executing-plans (làm tại chỗ) hoặc superpowers:subagent-driven-development (gắn nguồn, kiểm độc lập). Mỗi bước có ô `- [ ]` để theo dõi.

**Mục tiêu:** trong bảng thông tin thiết bị, mỗi dòng "Chức năng" và "Chi tiết" có một dấu ✓ / ≈ / ⚠ bấm được; bấm vào thì hiện popup nói rõ từng thông tin trong dòng là có nguồn, suy ra hay giả định, kèm tài liệu gốc (trích dẫn, link, ảnh thu nhỏ).

**Cách làm:**
- Nguồn chuẩn là các file gắn tay `web/prov/lines/<group>.json`. Khoá của mỗi dòng là hash của chữ tiếng Việt, nên dòng trùng nhau chỉ gắn một lần.
- Script mới `web/tools/make_prov.py` làm bốn việc: sinh sổ nguồn từ `research/*`, kiểm tra, xuất mỗi thiết bị một file JSON (nguồn được nhúng sẵn), và làm ảnh thu nhỏ.
- Viewer chỉ tải file của thiết bị khi thiết bị được chọn, và chỉ tải ảnh khi mở popup.

**Công nghệ:** Python 3 (stdlib; PIL cho bước ảnh), React 19, zustand 5, `<dialog>` gốc, CSS `.ze-*`.

**Spec:** §1–§3 của file này. Đây là bản người dùng duyệt ngày 2026-10-06, xem DECISIONS #34.

## Ràng buộc chung

- Chỉ đụng vào bảng thông tin thiết bị (`InfoPanel.tsx`). FLOW, nút trạng thái, "Nối với" và "Kích thước" giữ nguyên.
- `devices.json` và 4 file dữ liệu còn lại không đổi một byte. `make -C web compare-drafts` vẫn phải đạt.
- Lazy load: lúc mở trang không có request nào tới `/data/prov/`. Mỗi lần chọn thiết bị tạo tối đa 1 request JSON. Ảnh chỉ tải khi popup mở, ảnh lớn chỉ tải khi bấm vào ảnh thu nhỏ.
- Không bịa nguồn. Thiết kế ghi "giả định" thì không được nâng lên mức cao hơn. Chưa chắc thì xếp "suy ra" hoặc "giả định".
- Không bao giờ dùng `~/ideathon-toyobo/22_3_160.pdf` (DECISIONS #2). Không đăng đường dẫn máy (`/Users/`, `~/`).
- Ảnh của bên thứ ba: luôn ghi xuất xứ, luôn có link về trang gốc. web-11 phải ghi giấy phép CC BY-SA 3.0.
- Mọi chữ hiện ra đều có cả VI và JA. JA viết theo kiểu `public/i18n/devices.ja.json`: ngoặc nửa độ rộng, kết câu bằng 。, số giữ kiểu VI ("1 200").

## Điểm reviewer cần soi

1. **Đổi thiết bị nhanh khi file nguồn chưa tải xong:** badge không bao giờ được hiện nguồn của thiết bị trước (state gắn theo id).
2. **Vite dev trả `index.html` cho file thiếu:** loader coi mọi response không phải JSON là lỗi. Panel vẫn chạy bình thường, chỉ không có badge.
3. **Esc khi popup đang mở:** chỉ đóng popup, vẫn giữ thiết bị đang chọn. Esc lần hai mới bỏ chọn.
4. **Chế độ JA khi bản dịch chi tiết có số dòng khác VI:** panel quay về dòng VI (`makeJa`), badge vẫn đánh theo chỉ số dòng VI.
5. **Popup dài trên màn 1366×768 và 600 px:** cuộn bên trong popup, nút đóng luôn nhìn thấy. Ảnh hỏng thì hiện chữ alt, không vỡ bố cục.

---

## 1. Mức tin cậy và quy tắc gắn (hướng dẫn cho người gắn nguồn)

| Mức | Dấu | VI / JA | Khi nào dùng | Ref bắt buộc |
|---|---|---|---|---|
| `sourced` | ✓ | Có nguồn / 出典あり | Giá trị hoặc đặc điểm có trong tài liệu công khai: claim `cNNN` có trích dẫn, trang catalogue KM, ảnh web chụp đúng đặc điểm đó | ≥ 1 ref loại claim, figure hoặc photo |
| `derived` | ≈ | Suy ra / 導出 | Đo trên hình catalogue hoặc ảnh; tính từ số có nguồn (ghi công thức); quyết định thiết kế dựa trên nguồn (DECISIONS, specs) | ≥ 1 ref bất kỳ |
| `assumption` | ⚠ | Giả định / 仮定 | Không có tài liệu: agent chọn theo thực hành chung, hoặc thiết kế ghi "giả định" / "ước lượng" | ref không bắt buộc; `reason_vi` và `reason_ja` bắt buộc |

- **Mức của một dòng là mức yếu nhất** trong các fact của dòng (giả định < suy ra < có nguồn).
- **Một fact cho mỗi giá trị hoặc mỗi cơ sở độc lập.** "Thân trụ Ø520, mặt bích Ø640 × 50" có hai fact nếu Ø520 và Ø640 có cơ sở khác nhau. Các số cùng một cơ sở thì gộp vào một fact.
- **Mọi con số đứng riêng trong dòng phải xuất hiện trong `text_vi` của một fact** (kiểm P11). Số đi liền sau chữ cái Latin (B5, M24, PT100) là tên gọi nên không tính.
- `text_vi` dài tối đa khoảng 160 ký tự. Bắt đầu bằng giá trị hoặc đặc điểm, sau đó tới cơ sở, ví dụ: "D = 169 mm: đường kính vít ZE 155 A UTi theo bảng KM".
- `reason_vi` của một giả định viết theo mẫu: "Không có tài liệu công khai về …; chọn … vì …". Với fact suy ra, `reason_vi` là "Cách suy ra": công thức hoặc phép đo.
- Trước khi trích một ref phải mở ra đọc. Nếu ref là claim, giá trị hoặc đặc điểm phải nằm trong `quote` hoặc `claim`. Nếu ref là ảnh, đặc điểm phải nhìn thấy trên ảnh.
- Kiến thức chung về máy đùn (ví dụ "PET bị thuỷ phân nếu còn ẩm") mà không có tài liệu trong bộ nguồn thì xếp `assumption`, lý do "kiến thức chung về đùn PET; bộ nguồn không có tài liệu riêng".

## 2. Dữ liệu

### 2.1 Mã ref (sổ nguồn `web/build/prov/registry.json`, sinh bằng `make_prov.py registry`)

| Mã | Loại | Lấy từ |
|---|---|---|
| `c001` … `c070` | claim | `research/claims.jsonl` |
| `web-01` … `web-20` | photo | bảng `research/web/images.md`, ảnh `research/web/img/` |
| `cat-p01` … `cat-p30` | figure (cả trang) | `research/pages/pNN.png`; chú thích lấy từ tiêu đề "### Trang N" trong `research/pdf_catalog.md` |
| `crop-<tên file không đuôi>` | figure (cắt) | `research/pdf_crops/*.png`; số trang lấy từ tiền tố `pNN`, riêng `ze1*ut_*` là trang 9 |
| `img-<tên>` | figure (ảnh nhúng) | `research/pdf_images/*` |
| `spec-<mục>` | doc VI | `research/specs.md`, ví dụ `spec-1`, `spec-1.1` |
| `meas-<mục>` | doc VI | `research/pdf_measures.md`, ví dụ `meas-2.2` |
| `design-<mục>` | doc VI | `design/design.md`, ví dụ `design-3.1` |
| `anim-<mục>` | doc VI | `anim/design-anim.md` |
| `dec-<n>` | doc VI | mục đánh số trong `DECISIONS.md`; **không dùng `dec-2`** |
| `rev-<C/I/Mn>` | doc EN | `design/review-01.md` |
| `drev-<C/I/Mn>` | doc EN | `drawings/review-01.md` |
| `issue-<n>` | doc VI | bảng trong `drawings/design_issues.md` |

- **Ghim (pin):** ref tài liệu có thể ghim một dòng cụ thể, viết `"spec-1|Khoảng cách tâm"`. Chuỗi sau `|` phải xuất hiện trong đúng một dòng hoặc đoạn của mục đó; đoạn trích được đăng chính là dòng đó. Ref không ghim thì đăng khoảng 400 ký tự đầu của mục.
- **Link PDF catalogue:** `https://plastrading.com/wp-content/uploads/2018/03/ZE_twin-screw_extruders.pdf#page=N`.

### 2.2 File gắn tay `web/prov/lines/<group>.json` (nguồn chuẩn)

```json
{
  "version": 1,
  "group": "barrel",
  "lines": {
    "<sha1(vi)[:12]>": {
      "vi": "Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71).",
      "used_by": ["barrel_b1:details[2]", "barrel_b3:details[2]"],
      "status": "draft",
      "facts": [
        {"level": "sourced", "text_vi": "…", "text_ja": "…", "refs": ["c001"]},
        {"level": "derived", "text_vi": "…", "text_ja": "…", "refs": ["spec-1|Khoảng cách tâm"], "reason_vi": "…", "reason_ja": "…"}
      ],
      "seed": {"sources": ["<chuỗi source của parts.json>"], "refs": ["c001", "dec-9", "crop-p12_barrel_types_utx_vs_ut_250dpi"]},
      "notes": ""
    }
  }
}
```

- `status` đi theo thứ tự `draft` → `curated` (đã gắn) → `verified` (người khác đã kiểm). Khi gắn và kiểm, chỉ sửa `facts`, `status`, `notes` và thêm khối `verified`; khối `verified` có `by`, `at` và `review` (đường dẫn file bằng chứng).
- `used_by` và `seed` do `make_prov.py seed` ghi lại. Người gắn không sửa hai trường này.
- Một fact bị hạ mức thì ghi mức cũ vào `was`. Trường này không được đăng.

### 2.3 Dữ liệu đăng `web/web-check/public/data/prov/<device_id>.json`

```json
{
  "version": 1,
  "device_id": "barrel_b3",
  "lines": [
    {"kind": "function", "index": 0, "vi": "<chữ dòng>", "level": "derived", "facts": []},
    {"kind": "details", "index": 2, "vi": "…", "level": null, "facts": []}
  ],
  "sources": {
    "c001": {"kind": "claim", "title": "…", "url": "…", "quote": "…", "claim": "…", "value": 169, "unit": "mm", "confidence": "high"},
    "cat-p12": {"kind": "figure", "page": 12, "pdf_url": "…#page=12", "caption_vi": "…", "caption_ja": "…", "thumb": "/data/prov/img/cat-p12.t.jpg", "large": "/data/prov/img/cat-p12.l.jpg", "tw": 480, "th": 340},
    "web-02": {"kind": "photo", "title": "…", "page_url": "…", "shows_vi": "…", "shows_ja": "…", "shows_en": "…", "credit": null, "thumb": "…", "large": "…", "tw": 480, "th": 320},
    "spec-1|Khoảng cách tâm": {"kind": "doc", "label": "specs.md §1", "title_vi": "…", "title_ja": "…", "excerpt": "…", "excerpt_lang": "vi"}
  }
}
```

- `level` là `null` khi dòng chưa được gắn: dòng còn `draft`, hoặc build ở chế độ strict mà dòng chưa `verified`.
- Ảnh thu nhỏ có cạnh dài 480 px, ảnh lớn 1280 px, JPEG. Chỉ làm ảnh cho những ref có người dùng tới.

### 2.4 Kiểm tra (`make_prov.py check [--strict]`, sai thì exit 1)

| Mã | Quy tắc | Chỉ strict |
|---|---|---|
| P01 | Mọi dòng Chức năng/Chi tiết của mọi thiết bị không tổng hợp trong `build/data/devices.json` có entry; hash không trùng giữa các nhóm | |
| P02 | `sha1(vi)[:12]` khớp khoá, `vi` khớp chữ hiện tại của thiết bị | |
| P03 | Không còn entry thừa (dòng không còn thiết bị nào dùng) | ✓ |
| P04 | Mọi entry có `status` = `verified` | ✓ |
| P05 | Entry có `status` khác `draft` thì có ít nhất 1 fact và `level` ∈ {sourced, derived, assumption} | |
| P06 | Mọi ref tra được trong sổ nguồn, kể cả phần ghim (xuất hiện đúng một lần) | |
| P07 | `sourced` có ít nhất 1 ref loại claim, figure hoặc photo | |
| P08 | `derived` có ít nhất 1 ref | |
| P09 | `assumption` có `reason_vi` và `reason_ja` | |
| P10 | `text_ja` / `reason_ja` có kana hoặc kanji và không chứa chữ cái riêng của tiếng Việt | |
| P11 | Mọi con số đứng riêng trong dòng đều có trong `text_vi` của một fact | ✓ |
| P12 | File ảnh gốc tồn tại; ảnh thu nhỏ và ảnh lớn đã được làm | |
| P13 | Danh sách cấm: `22_3_160`, `ideathon`, `/Users/`, `~/` không xuất hiện trong dữ liệu đăng; không có ref `dec-2` | |
| P14 | Mọi ref tài liệu, ảnh, trang catalogue có tiêu đề hoặc mô tả JA trong `web/prov/sources.i18n.json` | ✓ |
| P15 | Mỗi file thiết bị ≤ 64 KB | |

Báo cáo ghi ra `web/build/reports/prov_check.json` và `prov_coverage.json` (số dòng và số fact theo mức, theo nhóm).

---

## Task 1: Sổ nguồn và kiểm token

**Files:**
- Create: `web/tools/make_prov.py` (`registry`, `selftest`)
- Create: `web/prov/sources.i18n.json` (`{}`)

**Interfaces:**
- Produces:
  - `build_registry() -> dict[str, dict]`, key là mã ref ở §2.1;
  - `resolve(ref: str, reg) -> dict | None`, xử lý cả ghim;
  - `tokens_of(source: str) -> list[str]`, chuẩn hoá token trong chuỗi `source` của `parts.json` thành mã ref.

- [ ] Chạy `python3 web/tools/make_prov.py selftest`. Kỳ vọng: in số ref theo loại, `unresolved 0`, exit 0. Nếu còn token không tra được thì exit 1 và in danh sách.
- [ ] Commit: `Prov: source registry from research files`

## Task 2: Seed các file nhóm

**Files:**
- Modify: `web/tools/make_prov.py` (`seed`)
- Create: `web/prov/lines/<group>.json` ×10

- [ ] Chạy `python3 web/tools/make_prov.py seed`. Kỳ vọng: 454 entry, 534 lượt dùng, 10 file. Chạy lại lần hai không đổi file nào (idempotent), và không đụng tới `facts` / `status` đã có.
- [ ] Commit: `Prov: seed draft line entries`

## Task 3: Build, kiểm tra, ảnh, Makefile

**Files:**
- Modify: `web/tools/make_prov.py` (`build`, `check`)
- Modify: `web/Makefile` (`prov`, `prov-seed`, `publish-prov`, `prov-negative`, `test-prov`; `all`, `publish`)

**Interfaces:**
- Produces:
  - `web/build/prov/out/<id>.json`;
  - `web/build/prov/out/img/*.t.jpg|.l.jpg`;
  - `web/build/reports/prov_check.json` dạng `{ok, failures[{code, key, device, detail}], warnings}`.

- [ ] `make -C web prov PROV_FLAGS=` → 186 file, mọi dòng `level: null`, exit 0.
- [ ] `make -C web prov` (strict) → exit 1 vì P04.
- [ ] `make -C web prov-negative`: năm lỗi cố ý (sửa một ký tự trong `vi`, ref `c999`, fact `sourced` chỉ có `spec-1`, xoá `text_ja`, chèn `22_3_160` vào một fact), lỗi nào cũng phải làm check exit 1.
- [ ] Commit: `Prov: per-device output, checks and publish step`

## Task 4: Model và loader lazy

**Files:**
- Create: `web/web-check/src/ui/provModel.ts`, `web/web-check/src/ui/prov.ts`, `web/tools/test_prov.mjs`

**Interfaces:**
- `provModel.ts`:
  - `ProvLevel = 'sourced' | 'derived' | 'assumption'`;
  - `weakest(facts) -> ProvLevel`;
  - `lineFor(prov, kind, index, vi) -> ProvLine | null`; trả `null` khi chữ lệch;
  - `countLevels(prov) -> Record<ProvLevel | 'unknown', number>`.
- `prov.ts`:
  - `loadProv(id) -> Promise<ProvDevice | null>`;
  - `useProv(id?: string) -> ProvDevice | null | undefined`; `undefined` là đang tải, `null` là lỗi hoặc không có dữ liệu.

- [ ] Chạy `node web/tools/test_prov.mjs`. Kỳ vọng mọi dòng PASS:
  - mỗi thiết bị có dòng thì có file;
  - `lineFor` khớp từng dòng;
  - `weakest()` trùng với `level` đã lưu;
  - mọi ref có trong `sources`;
  - ảnh tồn tại.
- [ ] Commit: `Viewer: lazy provenance loader`

## Task 5: UI badge và popup

**Files:**
- Create: `web/web-check/src/ui/Provenance.tsx`
- Modify:
  - `web/web-check/src/ui/InfoPanel.tsx` (dòng chức năng, các `<li>` chi tiết, hàng tổng)
  - `web/web-check/src/ui/text.ts` (khối `prov` trong `T` và `T_JA`)
  - `web/web-check/src/ui/ui.css`

- [ ] `npm run build && npm run lint` đạt.
- [ ] Chrome:
  - chọn `barrel_b3`: có đúng một request `/data/prov/barrel_b3.json`, chưa có request ảnh;
  - bấm badge thì popup mở; Esc đóng popup mà thiết bị vẫn được chọn;
  - chụp màn hình VI/JA.
- [ ] Commit: `Viewer: provenance badges and dialog`

## Task 6: Pilot khoảng 15 dòng, dừng lại để người dùng xem

- [ ] Gắn và kiểm các dòng của `barrel_b3`, `screws`, `melt_gear_pump`, `feed_hopper`.
- [ ] `make -C web publish-prov PROV_FLAGS=`.
- [ ] Chụp popup đưa người dùng xem, ghi phản hồi vào §1. **Chưa làm tiếp khi người dùng chưa đồng ý.**
- [ ] Commit: `Prov: pilot lines and style guide`

## Task 7–8: Gắn nguồn và kiểm độc lập theo nhóm

- [ ] Chia 12 lô theo nhóm (barrel 2, melt 2, feed 2, die, drive, control, vacuum, base + context, util). Mỗi lô: gắn, rồi chạy `make -C web prov PROV_FLAGS=` tới khi chỉ còn lỗi P04, rồi commit `Prov: curate <group> lines (N)`.
- [ ] Kiểm độc lập do agent khác làm, không phải người đã gắn nhóm đó:
  - đối chiếu từng fact ✓ với trích dẫn hoặc ảnh;
  - tính lại công thức của fact ≈;
  - hạ mức fact không có chứng cứ;
  - ghi bằng chứng vào `web/review/prov/verify-<group>.md`;
  - đặt `status: verified`.
  - Commit `Prov: verify <group>`.

## Task 9: Đăng bản strict

- [ ] `make -C web prov publish-prov` ở chế độ strict: "?" = 0, `compare-drafts` vẫn đạt.
- [ ] Commit: `Prov: publish verified provenance`

## Task 10: Hook tự kiểm và tài liệu

**Files:**
- Modify: `web/web-check/src/test/hooks.ts` (`provCheck`), `web/web-check/README.md`, `web/web-check/SELFTEST.json`

- [ ] `__ze.provCheck()` kiểm:
  - lúc `ready` chưa có request prov;
  - mỗi lần chọn thiết bị có đúng 1 request, chọn lại không có thêm;
  - `x_takeoff` không có request;
  - số badge = 1 + số dòng chi tiết;
  - chưa mở popup thì chưa có request ảnh;
  - Esc trong popup không bỏ chọn;
  - ở JA, chữ có kana/kanji.
- [ ] Commit: `Viewer: provenance self-check and docs`

## Task 11: Review độc lập và sửa

- [ ] Reviewer độc lập lấy mẫu ngẫu nhiên, ưu tiên fact ✓, rồi soát UI trên Chrome; ghi vào `web/review/prov/review-prov-01.md`. Sửa xong thì commit `PROV review round 1: fix …`.
