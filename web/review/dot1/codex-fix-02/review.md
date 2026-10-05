# Review Đợt 1 — focus bị che và X4120

Ngày: 2026-10-05. Phạm vi: hai lỗi trong plan người dùng đã duyệt.

## Thay đổi

- `src/scene/CameraRig.tsx`: focus dùng cùng bounding sphere, padding và khoảng fit hiện có. Chấm 15 tia qua tâm, tâm sáu mặt và tám góc bounding box; chỉ tính tia có hit bề mặt mesh đích thật. Raycast có bộ lọc phần ẩn, ghost và clipping hiện có.
- Giữ hướng với ít nhất ba mẫu hợp lệ và tỷ lệ nhìn thấy ≥80%. Thiếu mẫu thì giữ fit cũ. Khi bị che, thử góc ngang và độ nâng theo mức thay đổi góc tăng dần; nếu không đạt ngưỡng, chỉ đổi sang góc tốt hơn hướng hiện tại. Chuyển động dùng `setLookAt` mượt; không chấm điểm liên tục trong render loop.
- `src/store.ts`: truyền mesh của thiết bị/chi tiết vào focus. Thiết bị hoàn toàn ẩn dùng bounding box đầy đủ và bỏ chấm occlusion, giữ fallback trước đó. Tham số mesh của `zoomToBox` là tùy chọn.
- `tools/make_data.py`: X4120 giữ pos `[5.067, 2.021, -1.278]`, target `[4.12, 1.36, 0]`, lens 35 mm. Sinh lại dữ liệu, không export lại Blender.

## Build và dữ liệu

- `make -C web data verify publish`: thành công; 1209/1209 meshes mapped, missing 0, orphans 0. `web/build/reports/check.json`: `ok: true`, `failures: []`.
- Main chạy lại `npm run build` sau sửa fallback: TypeScript + Vite thành công. Còn cảnh báo chunk >500 kB đã có.
- Cả năm JSON `cut_states`, `devices`, `materials`, `node_map`, `rotors` trong build/public khớp byte.
- SHA-256 `cut_states.json`: `d7eaf81354614c522289822553d65a1afdc3790f8ef012013a3381cf37d15c85`.
- [Hồ sơ kiểm chứng](verification.json) ghi build, hash và kết quả đối chiếu dữ liệu.

## Codex Computer Use

URL: `http://127.0.0.1:5178/`, Codex In-app Browser. Thao tác thật bằng CUA; không dùng Chrome/Blender MCP và không dispatch WheelEvent để kiểm chứng đợt này. Viewport tạm 1366×768 và 1920×1080 đã trả về mặc định.

| Case | Kết quả và bằng chứng |
| --- | --- |
| F khi bình bị che, 1366 | Thân bình hiện rõ: [trước](focus-occluded-before-F-1366.jpg), [sau](focus-after-F-1366.jpg). |
| F khi vent dome che bình, 1920 | Thân bình hiện rõ: [trước](focus-vent-dome-before-F-1920.jpg), [sau](focus-after-F-1920.jpg). |
| Nút Phóng to, 1366 | Thân bình hiện rõ: [trước](focus-occluded-before-button-1366.jpg), [sau](focus-after-button-1366.jpg). |
| Cây thiết bị, vent dome, 1366 | [Trước](focus-vent-dome-before-tree-1366.jpg) bình bị dome che gần hết; [sau](focus-after-vent-dome-1366.jpg) thấy thân bình trụ và chân. |
| Double-click | 1366: [click thân bình đang rõ](focus-after-doubleclick-1366.jpg). 1920: kéo `[1330,600]→[1250,600]` làm ống/dome che phần giữa, double-click `[865,375]` lên phần thân còn lộ; camera chuyển sang góc rõ: [trước](focus-partial-occlusion-before-doubleclick-1920.jpg), [sau](focus-partial-occlusion-after-doubleclick-1920.jpg). Không click xuyên qua vật che kín. |
| Thiết bị đang rõ | F giữ hướng: [trước](focus-clear-before-F-1366.jpg), [sau](focus-clear-after-F-1366.jpg). |
| Alt chọn chi tiết | Info xác nhận `Chi tiết: vac_separator`; F focus đúng: [ảnh](focus-Alt-part-F-1366.jpg). |
| Thiết bị ẩn | X4120 ẩn `barrel_cover_c3` và `_hw`; focus từ cây và F vẫn giữ ẩn/bbox nét đứt, dùng fit fallback: [trước](hidden-cover-before-focus-1366.jpg), [cây](hidden-cover-focus-1366.jpg), [F](hidden-cover-F-1366.jpg). |
| X4120 | Toàn bộ mặt cắt barrel và hai tiết diện vít nằm trong khung: [1366](CUT_X4120-1366.jpg), [1920](CUT_X4120-1920.jpg). Quan sát ảnh: đáy cách mép dưới khoảng 68/95 px, vượt 24 px; đây là ước lượng thị giác, không phải phép đo pixel tự động. Không cần hạ target thêm. |
| FULL / CUT_Z_BARREL / X2450 / CUT_FEED | Chuyển trạng thái thành công; [FULL](FULL-1366.jpg), [Z](CUT_Z_BARREL-1366.jpg), [X2450](CUT_X2450-1366.jpg), [FEED](CUT_FEED-1366.jpg). |
| Chọn mặt cắt và wheel | Click phần đỏ của tiết diện vít X2450 chọn `screws`: [ảnh](X2450-pick-screws-1366.jpg). Scroll thật 0.02 page phóng lớn: [ảnh](X2450-wheel-zoom-1366.jpg). |
| FREE | Vào X=3000; Z mặc định 1200, slider lên 1250; flip đổi phía giữ và hình học đổi; Y mặc định 0. [entry](FREE-entry-1366.jpg), [Z1250](FREE-Z1250-1366.jpg), [flip](FREE-Z1250-flipped-1366.jpg), [Y0](FREE-Y0-1366.jpg). |
| Escape | Bỏ chọn thành công. |
| Console | 0 errors, 9 warnings `THREE.Clock` deprecated từ các lần reload/HMR: [log](console-warnings-errors.json). |

## Review Luna và main

- `explorer_subagents` review độc lập focus source/fallback và ảnh M7: đạt ngưỡng/cách chọn góc trong plan, issue đích ẩn đã sửa; không còn finding cần sửa. Ảnh trước/sau xác nhận vent dome che bình rồi thân bình hiện rõ.
- `explorer_session` review độc lập preset/generated data và ảnh X4120: nguồn và dữ liệu khớp, framing đáp ứng mục tiêu; không cần đổi target thêm.
- Main đọc lại thay đổi cuối, kiểm tra build/data và trực tiếp kiểm chứng partial-occlusion double-click 1920.

## D13

**Đạt có ghi chú**, theo tiêu chí `web/PLAN-DOT1.md` D13. Reviewer độc lập: `gpt-5.6-luna / explorer_session`; main đọc tiêu chí và kiểm tra lại hai ảnh X4120 với reference. Không có finding C/I trong tập ảnh này.

| Trạng thái | Kết luận visual của Luna |
| --- | --- |
| FULL 1366/1920 | Toàn máy và platform rõ, bố cục hero tương ứng `out/renders/ze155-hero.png`. |
| CUT_Z_BARREL | Hai dãy vít, các phần chuyển tiếp, mặt thép đỏ vân chéo và fill đọc được; không có cover lớn che mặt cắt so với `anim/look/A1a-S04-f1161-ev-r2.png`. |
| CUT_X2450 | Lỗ số 8, hai biên dạng vít, bore tối và nhựa hổ phách rõ; framing chặt hơn `anim/look/A1a-x2450-S05b-ev-r2.png` nhưng nội dung mặt cắt đủ. |
| CUT_X4120 1366/1920 | Hai tiết diện vít, barrel và ngữ cảnh dome rõ so với `anim/look/A1a-x4120-S07b-ev-r2.png`; mặt cắt barrel không crop đáy. |
| CUT_FEED | Cột và mặt cắt đọc được so với `anim/look/A1a-feedcol-ext-wb.png`; crop phễu gần toolbar là ghi chú M, ngoài phạm vi sửa. |
| FREE entry | Mặt cắt nhỏ do giữ camera FULL; ghi chú M của hành vi hiện tại. |
| FREE Z1250 | Mặt cắt Z và clipping tương ứng label; không thấy cap/duplicate/occlusion regression. |

`web/web-check/SELFTEST.json`: `summary.D13` và `criteria.D13.ok` đã chốt `true`, kèm `review.status: passed_with_notes`, reviewer, ngày, môi trường, reference và ảnh mới. Giữ provenance gốc, raw, ảnh cũ và mọi kết quả tiêu chí khác; đợt này không chứng nhận lại hiệu năng D1–D15.

## Giới hạn và việc còn lại ngoài phạm vi

- CUT_FEED còn crop phễu gần toolbar; nằm ngoài phạm vi sửa đã duyệt.
- FREE giữ camera của FULL khi vào trạng thái, nên mặt cắt mặc định nhỏ; không đổi camera FREE trong đợt này.
- Pinch hai ngón chưa kiểm chứng bằng input thật: CUA không cung cấp API pinch hoặc scroll giữ modifier được tài liệu hóa. Bằng chứng WheelEvent mô phỏng trong SELFTEST cũ không được coi là kiểm chứng pinch mới.
- Đợt 2 chưa triển khai.
