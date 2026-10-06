# Review FLOW "Quy trình: hạt → film", vòng 1

Reviewer độc lập, 2026-10-06. Không sửa code, dữ liệu hay plan. Chấm theo `web/PLAN-FLOW.md` §1–§9, có tính các thay đổi ở §10.

**Môi trường:**
- Chrome 154 riêng, profile mới, cổng 9411, điều khiển qua CDP (puppeteer). Không dùng chrome-devtools MCP.
- `http://127.0.0.1:5178/?selfcheck=1`, DPR 1, viewport 1920 × 1080 và 1366 × 768. Màn hình 120 Hz, Apple M3 Pro.
- Ảnh và lấy mẫu pixel đều chạy sau `__ze.freeze(true)`.
- Click, double-click, hover, phím F / Esc và bấm nút toolbar / cây đều là input thật (`page.mouse`, `page.keyboard`).

**Không chạy:** `publish`, Blender, `make all`. Đã chạy `make -C web data verify`; lệnh này chỉ ghi vào `web/build/` (nằm trong `.gitignore`).

Ảnh của reviewer ở `web/review/flow/reviewer/`; dưới đây tên file tính từ thư mục đó.

## Kết luận

**Đạt có điều kiện. 0 C, 2 I, 4 M.**

- Dữ liệu, hook, hiệu năng, hồi quy, nhãn và thao tác đều đạt khi đo lại (F1–F6, F8–F10).
- F7 đạt một phần. Cả 7 cụm nhìn thấy liền mạch và khớp ảnh tham chiếu. Riêng cụm trục cán còn lỗi: tấm film vẽ đè lên mặt cắt của trục cán (I1).
- Cần sửa I1 và I2 trước khi đưa người dùng xem.

## F1–F10

| # | Kết quả | Số đo của reviewer |
|---|---|---|
| F1 | **Đạt** | `make -C web data verify` exit 0; `check.json` có `ok: true`, `failures: []`, 1209/1209 mesh, missing 0, orphans 0, FLOW hiện 329 node. 5 file `build/data/*.json` mới sinh trùng từng byte với `web-check/public/data`. GLB 5 793 436 / 1 982 388 B. `selfcheck()` trong FLOW: unknown 0, missing 0, orphans 0, devices 190, `rayUnfiltered` 0. Danh sách FLOW không có tên nào nằm ở hai danh sách; trục vít A ẩn, B hiện; van chỉ hiện bộ CHẠY |
| F2 | **Đạt** | `setState('FLOW')` resolve ra `'FLOW'`. `timeState('FLOW')` 16,5 / 17,1 ms (lần đầu 16,5–19,3). `cutRoundTrip()`: ok, `bad` [], `flowLeft` true, 0 `gl.clippingPlanes`, 0 freePlane. `rayUnfiltered` 0. Thử dồn: tải lại, bấm FLOW → CUT_FEED → FLOW → FREE → FLOW cách nhau 60 ms khi phần bên trong còn đang tải → vẫn 1 mesh hạt, 27 mesh nhựa, 29 renderOrder, `leftovers` 0, round trip ok |
| F3 | **Đạt** | `capCheck('FLOW', d)` 3/3 lần cho cả 5 thiết bị: `feed_throat` 9/9, `barrel_b3` 254/254, `melt_gear_pump` 438/438, `die_body_lower` 129/129, `ctx_roll_middle` 67/67. Thêm một click CDP thật lên pixel mẫu của từng thiết bị: chọn đúng cả 5 |
| F4 | **Đạt** | `pelletTest(2)`: chậm z01 0,06334 m/s (kỳ vọng 0,06338, sai 0,06 %), z02 0,04222 (sai 0,07 %); thực 1,2609 / 0,8406 m/s (sai 0,5 %); tắt: 0 toạ độ đổi; `maxPelletX` 1,8917; `minPelletZ` 0,0055; 2 000 hạt = N. Đo độc lập từ `instanceMatrix` trong 2 s: z01 0,0635, z02 0,0423 m/s |
| F5 | **Đạt** | `fillProbe()`: 27 mesh, chương trình `ze-fill-curtain/die/line/line-cap` + `ze-sheet`, `leftovers` 0. `fillColorAt(1.0,'phase')` #DBD6C2 = màu hạt; `(2.5,'phase')` #D95709 = màu nhựa; `(5.9,'heat')` #DC4D27 = heat(285). Vân trôi: chụp 6 khung không freeze, cách nhau 0,29 s, ở đầu xi lanh / van. Pha của sọc chu kỳ 0,12 m giảm đều −0,34 rad mỗi khung, tức vân trôi về +X (bên trái màn hình). Đo được khoảng 22 mm/s, kỳ vọng 31,7 mm/s; phần thiếu nhiều khả năng do khung bị dừng khi chụp. `F5-drift-valvesc-t0.png`, `F5-drift-valvesc-t1s.png`. Vân khá mờ (độ sáng × 0,85–1, đúng như spec) |
| F6 | **Đạt** | `sheetProbe(1)`: vật liệu `ze-sheet`; tốc độ 0,41601 m/s (sai 0,19 %; đo theo đồng hồ uniform `uRollT`); khi tắt bằng 0; ở s = 0: pha #D95709 (hổ phách), nhiệt #E8903B = heat(250) |
| F7 | **Đạt một phần** | Cả 7 mục đều thấy rõ ở 1920 và 1366 (xem mục F7 bên dưới). Lỗi: tấm film đè lên mặt cắt trục cán (I1); lõi trục cán thành "lỗ" xám (M3). Quét 14 400 tia ở 13 góc nhìn: không có cặp mặt trước trùng nhau của phần ngoài với bản rỗng, không thấy z-fighting do danh sách FLOW gây ra |
| F8 | **Đạt** | Preset FLOW: 119,9 fps (màn 120 Hz), 743 draw call, 1 062 937 tam giác, heap 120–126 MB. 1366 cho số như vậy. Góc xiên / cột cấp liệu / khuôn: 503 / 230 / 229 call. Precompile 135–157 ms ở mọi lần tải. *Ghi chú:* một lần duy nhất, lần đầu chạy profile Chrome mới, precompile mất 1 717 ms (> 1,5 s của §5); không lặp lại được, kể cả với `--disable-gpu-shader-disk-cache` (152 ms) |
| F9 | **Đạt** | D4 6/6, mỗi ca 3 lần: Z_BARREL/b3 40/40, X2450/b3 89/89, X2450/screws 32/32, X4120/b5 33/33, FEED/throat 22/22, FREE x 3,0/b4 58/58. D6 ok. D7: `timeState` cả 7 trạng thái 16,6–18,7 ms. Console 0 lỗi; mỗi lần tải chỉ 1 cảnh báo "THREE.Clock … deprecated" (đã biết). 244 request qua 4 lần tải, tất cả tới `http://127.0.0.1:5178`. `selftest()` 35 s: D1–D9, D14, F2–F6, F8 đều true. `SELFTEST.json` có mục `flow`. Ảnh 6 trạng thái cũ vẫn nắp đỏ và vân chéo như Đợt 1 |
| F10 | **Đạt** | Nhãn và tooltip của 7 nút, VI và JA, khớp từng chữ với §4.1. 3 nút hướng: "Cắt ngang / Bổ dọc / Cắt nằm", 「横断 / 縦断 / 水平」; tooltip giữ chữ trục. Không nút nào còn toạ độ. Toolbar ở 1920: FULL 1 hàng, các trạng thái khác 2 hàng (FLOW 75 px). Ở 1366: FULL 2 hàng, các trạng thái khác 3 hàng (FLOW 93 px VI / 91 px JA). Không nút nào bị cắt chữ, không tràn ngang. Đổi FLOW sang Nhiệt độ → JA → VI: vẫn ở chế độ nhiệt, chú thích và `aria-pressed` đúng |

### F7: soát bằng mắt

| Mục | Ảnh | Nhận xét |
|---|---|---|
| Hạt trong cột cấp liệu | `flow-feedcol-phase-1920.png`, `-1366.png`, `flow-hopper-phase-1920.png` | Hạt rơi trong ống xả (ống đã cắt, thấy mặt trong), qua phễu và họng rồi xuống rãnh vít. Ở chế độ nhiệt hạt rơi màu xanh 30 °C |
| Trục vít B trong lỗ | `flow-pellets-phase-1920.png` | Vít đen nằm trong eo lỗ, hạt nằm thành lớp dưới đáy |
| Màu đổi ở khối nhào | `flow-melt-phase-1920.png`, `-1366.png` | Hạt nhỏ dần và chuyển hổ phách ở X 1,52–1,90 trên khối nhào; vùng hút khí là lớp nhựa dưới đáy |
| Van, lọc, bơm, ống | `flow-valvesc-phase-1920.png`, `flow-scdisc-phase-1920.png`, `flow-pump-phase-1920.png`, `flow-pipe-phase-1920.png` | Kênh nhựa liền từ đầu vít qua van, đĩa lọc (trong hộp ghost xanh), bơm và bộ trộn tĩnh. **Bơm khớp rất sát** `A1b-S10-f2701-ev-r3.png`: bánh răng, nhựa trong hốc răng, kênh vào / ra; FLOW dùng màu xám thay cho đỏ (§10.3) |
| Khuôn A-A có nhựa | `flow-die-phase-1920.png`, `-1366.png` | **Khớp** `A1b-S12-f3351-ev-r2.png`: đầu nhựa tròn ở adapter, khe mảnh màu cam, rãnh choker, cụm chỉnh môi phía trên |
| Màn nhựa | `flow-nip-phase-1920.png`, `flow-nipOblique-*.png` | Dải cam từ môi khuôn tới khe giữa hai trục cán |
| Tấm ôm trục, ra băng tải | `flow-sheet-phase-1920.png`, `flow-rolls-phase-1920.png` | Đường đi đúng: ôm trục giữa, ôm trục trên, sang con lăn dẫn, xuống dốc rồi chạy trên băng tải. Màu hổ phách chuyển sang PET trong (pha), 250 °C xuống xanh (nhiệt). **Nhưng tấm vẽ đè lên mặt cắt của trục cán (I1), lõi trục thành "lỗ" xám (M3)** |
| Cột cấp liệu ↔ `A1a-feedcol-ext-wb.png` | `flow-feedcol-phase-1920.png` | Cùng bố cục: ống xả cong, phễu, họng. Ảnh tham chiếu là mặt ngoài, ảnh FLOW là mặt cắt |
| Khối đặc | `flow-preset-phase-1920.png`, `flow-oblique-phase-1920.png` | Không khối đặc nào phủ kênh nhựa. Khung đế và hộp số / động cơ (FLOW_SOLID_CLIP) thành mảng gạch chéo lớn nhưng nằm ngoài đường vật liệu (đã ghi lý do trong §10.7) |

## Lỗi

| ID | Mức | Ở đâu | Mô tả và bằng chứng | Cách sửa đề xuất |
|---|---|---|---|---|
| I1 | I | FLOW, cụm trục cán, cả 1920 / 1366, VI / JA; thấy cả ở preset. Rõ nhất khi nhìn xiên và ở chế độ nhiệt | **`ctx_sheet` vẽ đè lên mặt cắt của trục giữa và trục trên.** Mặt cắt gạch chéo bị phủ một lớp màu: hổ phách gần khe cán (pha), hoặc dải vàng / xanh có sọc (nhiệt). Khi ẩn tạm `ctx_sheet` thì mặt cắt sạch, tức lỗi do tấm gây ra. **Nguyên nhân:** nắp chạy lúc runtime vẽ ở độ sâu của thành xa (README "Cap depth bias"). Tấm ôm phía +X của trục ở r 0,399–0,402 m, z 0…1,05, gần như trùng thành trục r 0,400 m, nên ở nhiều pixel tấm thắng phép thử độ sâu. Đây là artefact thứ 2 của M3 Đợt 1, nặng hơn ở FLOW vì tấm giờ có màu. Bằng chứng: `I1-sheet-over-roll-cap-with-vs-without.png` (trái: có tấm, phải: ẩn tấm), `flow-nipOblique-heat-1920.png`, `flow-nip-phase-1920.png`, `flow-obliqueDie-phase-1920.png`, `flow-sheet-heat-1920.png` (trục trên phủ màu xanh), `m3-FLOW-sheet-phase-1920.png` | **Web code (SheetMaterial):** trong fragment shader của `ze-sheet`, lấy giao điểm P của tia camera → fragment với mặt phẳng FLOW. Nếu fragment nằm sau mặt phẳng (z > 0) và P nằm trong một vòng tròn trục cán (tâm của 3 trục, r 0,4005) thì `discard`. Cách này giả lập một nắp nằm đúng trên mặt phẳng. Tâm trục giữa và trục trên đã có trong `flow.sheet.path_three_xy`; tâm trục dưới thêm vào dữ liệu. Có thể làm tương tự cho FREE Y |
| I2 | I | FLOW, dòng chú thích toolbar, mọi viewport, VI / JA | **Hai ô "nhựa" khác màu cùng một hàng.** Chú thích FLOW có "Nhựa chảy" #D95709; ngay bên cạnh, "Màu nắp cắt" vẫn có "Nhựa nóng chảy" #ED9E38. Ở JA cả hai cùng ghi **「溶融樹脂」** nhưng hai màu khác nhau. Trong FLOW không có mesh nào dùng nắp lớp `melt`: đếm nắp đang hiện cho steel 267, screw 66, rubber 45, insulation 4, melt 0. Vì thế ô này vừa thừa vừa trái với màu nhựa thật của FLOW. Bằng chứng: `I2-legend-two-melt-swatches-1366-ja-vi.png` | **Web code (`Toolbar.tsx`):** ở FLOW bỏ `melt` khỏi `CAP_ORDER`, hoặc chỉ liệt kê lớp nắp có trong trạng thái đang xem. Mỗi lỗi ≤ 15 phút |
| M1 | M | Vào FREE từ FLOW (và từ các trạng thái cắt), hướng "Cắt ngang" | FREE giữ nguyên camera cũ. Từ camera FLOW (nhìn dọc +z), mặt cắt X = 3 000 nằm gần như song song tia nhìn, nên không thấy nắp, chỉ thấy nửa máy x ≤ 3 m. `state-FREE-vi-1920.png`, `free-X-from-FLOW-ja-1366.png`. (Từ FULL thì đã thấy nắp, xem mục M4 bên dưới) | **Web code:** khi vào FREE hoặc đổi hướng, nếu \|n · hướng nhìn\| nhỏ hoặc mặt cắt quay lưng thì xoay camera về phía mặt giữ lại. Hoặc khi vào từ FLOW / CUT_FEED thì mặc định hướng "Bổ dọc" Y = 0 |
| M2 | M | CUT_FEED, preset, 1920 và 1366 | Mép trên phễu (y 1,95 m) chiếu lên màn ở y = 59 px khi toolbar đáy ở 69 px (1920), và y = 42 px khi toolbar đáy ở 87 px (1366). Miệng ống xả nằm ở y ≈ 1 px. `state-CUT_FEED-vi-1366.png`, `state-CUT_FEED-vi-1920.png` | **Dữ liệu (camera):** trong `CAMERA_OVERRIDES` của CUT_FEED, hạ target hoặc lùi camera để mép phễu nằm dưới toolbar ở 1366 |
| M3 | M | Trục cán ở FLOW và FREE Y = 0 | Lõi rỗng của trục cán (r 0,15 / 0,19 m, hai đầu hở) hiện thành đĩa xám sáng, lệch tâm khi nhìn xiên, trông như một lỗ xuyên qua trục. `m3-FLOW-rolls-phase-1920.png`, `m3-FREE-Y0-sheet-1920.png`, `flow-sheet-phase-1920.png` | **Blender only:** đóng lõi hoặc dựng trục bên trong trục cán. Tạm thời ở web: một đĩa phụ (helper) che lõi trong các trạng thái cắt |
| M4 | M | FLOW, mặt cắt xi lanh ở 3 gối đỡ (x ≈ 1,2 / 3,2 / 5,2 m) | Ngay dưới lỗ xi lanh có một ô vuông màu cam cá hồi #F79F71, trông như một mảng nhựa chảy. Đó là tấm đệm đồng `barrel_support_N_3` (`ze_copper`) nằm lấn vào thể tích thân xi lanh. Vì nắp vẽ ở thành xa, tấm đệm hiện xuyên qua mặt cắt; ẩn tạm tấm đệm thì pixel trở về xám gạch chéo #7A8086. `M-copper-pad-through-barrel-cap-with-vs-hidden.png`, `flow-barrel-phase-1920.png` | **Blender:** sửa tấm đệm để không chồng lên thân xi lanh. Tạm thời ở web: lớp FLOW đổi `ze_copper` của `barrel_support_*` sang xám thép |

Tổng: 0 C, 2 I, 4 M.

## 5 lỗi đã biết

| Lỗi | Trạng thái | Bằng chứng |
|---|---|---|
| CUT_FEED: phễu nằm dưới toolbar | **Còn**, ở cả 1920 và 1366 (M2) | `state-CUT_FEED-vi-1366.png`; số chiếu ở M2 |
| M4: vào FREE thấy mặt cắt quay lưng | **Đã sửa khi vào từ FULL**: camera FULL ở phía +X, nắp X = 3 000 quay về phía người xem (`free-enter-from-FULL-vi-1920.png`). **Còn ở dạng khác** khi vào từ FLOW: mặt cắt nằm song song tia nhìn (M1) | `state-FREE-vi-1920.png`, `free-X-from-FLOW-ja-1366.png` |
| M3: nắp trục cán | **Còn cả hai artefact.** Đĩa xám ở lõi (M3). Tấm film vẽ đè lên nắp, ở FLOW nặng hơn vì tấm có màu (I1) | `m3-FREE-Y0-sheet-1920.png`, `m3-FLOW-rolls-phase-1920.png`, `I1-…png` |
| M6: chấm đầu dòng và id thô ở bảng thông tin | **Đã sửa.** `.ze-link` có `display: inline`, chấm đứng cạnh dòng đầu. `ctx_floor` hiện "Sàn nhà xưởng" / 「工場床面」 | `m6-info-melt_stand_pump-vi-1920.png`, `…-ja-1920.png` |
| M5: toolbar 7 nút ở 1366 px | **Đã cải thiện, vẫn 3 hàng**: FULL 2 hàng (65–67 px); trạng thái cắt 3 hàng (85–87 px); FLOW / FREE 3 hàng (91–93 px). Vẫn trong giới hạn F10. Panel 236 / 272 px; khi chọn thiết bị, bảng thông tin cao tới y ≈ 760 và che khoảng 1/3 bên phải canvas | `state-*-1366.png`, `ix-tree-FLOW-ja-1366.png` |

## Thao tác: 7 trạng thái × 1920 / 1366 × VI / JA

Đã chạy bằng input thật cho mỗi tổ hợp. Đều đạt.

**Các bước:**
1. Bấm nút trạng thái.
2. Hover lên một pixel của thiết bị: viền xanh, và mục cây cùng sáng.
3. Click: chọn đúng; tiêu đề bảng thông tin theo đúng ngôn ngữ.
4. Esc: bỏ chọn.
5. Double-click thật: target về tâm hộp, sai 0–1 mm.
6. Nút "Về góc nhìn của trạng thái", rồi F: zoom đúng.
7. Bấm mục cây "Bơm bánh răng nhựa" / 「メルトギアポンプ」: chọn và zoom tới bơm.

**Thiết bị dùng:**
- FULL `vac_separator`;
- CUT_FEED `feed_throat`;
- Z_BARREL và X2450 `barrel_b3`;
- X4120 `barrel_b5`;
- FLOW `barrel_b3`;
- FREE `melt_gear_pump`.

Ảnh: `ix-{hover,select,dbl,tree}-{FLOW,CUT_FEED,FREE}-{vi,ja}-{1920,1366}.png`.

**Ghi chú:**
- Một lần hover ở CUT_FEED VI 1366 không sáng viền. Chạy lại 2 lần thì đúng; không coi là lỗi.
- FREE 3 hướng (bấm nút thật): số đo "X = 3 000 mm / Y = 0 mm / Z = 1 200 mm" và tooltip phía giữ lại đúng ở VI và JA. Nắp ở FREE màu đỏ: màu xám của FLOW không lọt sang FREE.
- FLOW → FREE → FLOW: `flowProbe` trước và sau giống nhau (27 mesh, 29 renderOrder, hạt hiện, giữ chế độ nhiệt). Trong FREE: lớp FLOW tắt, 0 mesh FLOW.

## Đã kiểm, không có lỗi
- **Dữ liệu FLOW:** các trạng thái cũ chỉ đổi `label_vi` và thêm `tooltip_vi`; `version` 1, `flow_version` 1.
- **Hạt:** đổi màu ngay cả khi đang freeze (ghi lại mỗi khung). Rotor "Tắt" và `freeze` làm hạt, sọc, vít đứng yên. Chỉ có 1 InstancedMesh, không raycast, `rayUnfiltered` 0.
- **Chọn trong FLOW:** viền và bbox hiện đúng trên phần đã cắt và phần cắt sẵn.
- **Không lỗi hiển thị:** ghost bộ lọc trong suốt, không che kênh nhựa; không có bản ngoài hiện cùng bản rỗng (vòm, đầu, van, bộ lọc, bơm, khuôn).

## Kiểm lại sau sửa (vòng 1)

Reviewer, 2026-10-06, kiểm commit `b84deb1` (PLAN-FLOW §10 mục 9).

**Môi trường:** như vòng 1. Chrome riêng, profile mới, cổng 9411, tải lại trang trước khi đo. Không sửa code, dữ liệu hay plan.

**Kiểm dữ liệu:** `make -C web data verify` exit 0, `failures: []`. 5 file `public/data` trùng từng byte với bản vừa sinh.

Ảnh ở `web/review/flow/reviewer/recheck-01/`.

**Kết luận mới: Đạt.** 0 C, 0 I, 3 M:
- M1 còn một phần;
- M3 chỉ sửa được trong Blender;
- một M mới rất nhỏ (N1).

I1, I2, M2, M4 đã sửa. F7 nay đạt; vẫn còn M3 (lõi trục cán).

| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| I1 tấm đè mặt cắt trục cán | **Đã sửa** | Lấy mẫu lưới 120 × 68, giữ các pixel mà tia chạm đầu tiên là mặt sau (nắp) của `ctx_roll_*`. So từng pixel giữa ảnh có tấm và ảnh ẩn tấm: **0 pixel nắp đổi màu** ở 5 góc nhìn (obliqueDie, nipOblique, rolls, sheet, nip) × pha / nhiệt × 1920. Ở 1366 cũng 0, trừ 1 pixel mép ở góc "sheet". Tấm vẫn hiện đúng ở phần ôm ngoài mép trục, đoạn sang con lăn dẫn và trên băng tải. `sheetProbe` trong `selftest` vẫn đạt. `I1-*-{phase,heat}-{1920,1366}.png`, ví dụ `I1-nipOblique-heat-1920.png`, `I1-sheet-heat-1920.png`, `I1-obliqueDie-phase-1366.png` |
| I2 hai ô nhựa ở chú thích | **Đã sửa** | Ở FLOW, "Màu nắp cắt" chỉ còn Thép, Trục vít, Cao su, Cách nhiệt (JA: 鋼, スクリュー, ゴム, 断熱材), ở cả pha và nhiệt, 1920 và 1366, VI và JA. CUT_Z_BARREL và FREE vẫn giữ "Nhựa nóng chảy" / 溶融樹脂 #ED9E38. `I2-toolbar-FLOW-{phase,heat}-{vi,ja}-{1920,1366}.png` |
| M1 vào FREE không thấy mặt cắt | **Sửa một phần** | **Khi vào FREE (đạt):** FLOW → FREE "Cắt ngang" chuyển sang preset FULL, thấy nắp. FLOW → FREE "Bổ dọc" giữ góc FLOW, thấy 140 mẫu nắp. FLOW → FREE "Cắt nằm" chuyển sang **preset CUT_Z_BARREL** (971 mẫu nắp), không phải FULL như §10.9 ghi: FULL có \|hướng · n\| = 0,28 < 0,3 nên bị bỏ qua. Cách chạy này hợp lý; chỉ cần sửa lời trong §10.9. FULL → FREE X và CUT_X2450 → FREE X không đổi camera, đúng yêu cầu. CUT_FEED → FREE X chuyển sang FULL. **Còn lại (M):** đổi hướng ngay trong FREE thì camera không xoay. Vào FREE "Bổ dọc" từ FLOW rồi bấm "Cắt ngang": camera vẫn ở góc FLOW, mặt cắt X nằm dọc tia nhìn, chỉ 16 mẫu nắp, không đọc được. Đề xuất: gọi `faceFreeCut` cả khi đổi trục trong `setFree` (web code). `M1-FLOW-to-FREE-{X,Y,Z}-vi-1920.png`, `M1-FULL-to-FREE-X-vi-1920.png`, `M1-X2450-to-FREE-X-vi-1920.png`, `M1-FEED-to-FREE-X-vi-1920.png`, `M1-FREE-switch-to-X-after-FLOW-vi-1920.png` |
| M2 phễu CUT_FEED dưới toolbar | **Đã sửa** | Camera mới: pos [1,67; 2,692; −3,166], 40 mm. Toạ độ chiếu lên màn: mép phễu y 511–532 px với toolbar đáy 70 px (1920), và y 363–378 với đáy 86–88 (1366). Khuỷu ống xả (−0,45; 2,45) ở y 201 (1920) và y 143 (1366), nằm giữa hai panel. Phần ống thẳng đứng phía trên khuỷu vẫn đi ra khỏi mép trên, chấp nhận được. VI và JA cho số như nhau. D4 CUT_FEED/feed_throat 3/3 lần đạt, 10/10 pixel nắp, click chọn đúng. `M2-CUT_FEED-{vi,ja}-{1920,1366}.png` |
| M3 lõi trục cán | **Chưa sửa** (Blender only, như builder đã ghi) | Đĩa xám vẫn thấy trong `I1-sheet-phase-1920.png` |
| M4 tấm đệm đồng | **Đã sửa ở FLOW** | Trong FLOW, `barrel_support_1..3_3` có màu #8E959C. Ô dưới lỗ xi lanh nay là xám sáng, không còn màu cam. FULL, CUT_Z_BARREL và FREE vẫn #B8734D. *Ghi chú:* tấm đệm vẫn chồng lên thân xi lanh trong mô hình, nên ở FREE Y = 0 vẫn thấy ô đồng xuyên qua mặt cắt đỏ. Gốc lỗi ở Blender, ngoài phạm vi FLOW. `M4-support-before-FLOW-after-FLOW-FREE.png` (trái: FLOW trước sửa; giữa: FLOW sau sửa; phải: FREE Y = 0), `M4-FLOW-barrel-phase-1920.png` |
| **N1 (mới, M)** | Màn nhựa lộ qua nắp trục giữa | Ở góc nhìn xiên vào khe cán, một đường cam mảnh khoảng 1 px chạy chéo qua mặt cắt trục giữa. Ẩn tạm `ctx_melt_curtain` thì đường này mất. Cùng cơ chế với I1: màn nhựa chạm thành trục, và nắp vẽ ở thành xa. Trước đây lớp tấm phủ lên nên không thấy. Rất nhỏ. Đề xuất: áp cùng phép `discard` của I1 cho vật liệu `ze-fill-curtain` (web code). `NEW-curtain-line-through-roll-cap-with-vs-hidden.png` (trái: có màn; phải: ẩn màn), `I1-nipOblique-heat-1920.png` |

**Hồi quy:**
- `__ze.selftest()` (34,5 s): D1–D9, D14, F2–F6, F8 đều true.
  - D4 6/6: CUT_FEED/throat 10/10, Z_BARREL/b3 40/40, X2450/b3 89/89, X4120/b5 33/33, X2450/screws 31/31, FREE x 3,0/b4 56/56.
  - F8: 120 fps, 743 call, 1 062 937 tam giác, heap 136 MB, precompile 535 ms (profile mới).
  - `selfcheck`: unknown 0, missing 0, orphans 0, `rayUnfiltered` 0, devices 190.
- Console 0 lỗi; chỉ có cảnh báo "THREE.Clock … deprecated" đã biết.
- 62 request, tất cả tới `http://127.0.0.1:5178`.

Tổng sau sửa: 0 C, 0 I, 3 M (M1 phần đổi hướng trong FREE, M3 Blender, N1).
