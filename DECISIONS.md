# Quyết định của orchestrator

Theo yêu cầu: tự làm, tự review, không hỏi lại. Mọi quyết định thay người dùng đều ghi ở đây.

## 2026-10-04
1. **Đọc phiên cũ:** chỉ đọc file `41763e1d-24a1-45fd-a999-5c69a2c1f244.jsonl`, đúng yêu cầu. Cách làm của phiên đó được chép vào `METHOD.md`, phần code tham chiếu nằm ở `tools/gx200_reference/`.
   - Phiên này là bản fork của `gx200-spike-b5`, nên có cả quá trình dựng (10:31–11:18 UTC, 75 lệnh Blender) lẫn phần animation sau đó.
2. **Không dùng `~/ideathon-toyobo/22_3_160.pdf`.** Đây là bài báo về màng PET co nhiệt, chỉ xác nhận chuỗi máy đùn → T-die → trục làm nguội, không có thông số máy. Đây là tài liệu của người dùng nên không đưa lên web.
3. **Ứng dụng giả định:** đùn tấm hoặc màng trực tiếp (PET hoặc PP) với trục vít đôi có hút chân không, lọc chảy (screen changer), bơm bánh răng (melt pump), T-die, rồi trục làm nguội (chill roll).
   - Lý do: catalogue ZE có mục "film and sheet production … slot die, smoothing roll", và đùn PET bằng trục vít đôi có hút chân không là ứng dụng phổ biến.
4. **ZE 155/34D:** đường kính vít 155 mm, chiều dài gia công 34D ≈ 5 270 mm. Catalogue có các đoạn xi lanh 4D và 6D, nên dự kiến chia 1 đoạn 4D cộng 5 đoạn 6D (4 + 30 = 34D). Designer được chỉnh lại nếu research cho thấy khác.
5. **Hệ trục (`BRIEF.md`):**
   - +X theo chiều dòng chảy, X = 0 ở mặt xi lanh phía hộp số;
   - +Y là phía người vận hành;
   - Z = 0 ở sàn.
   - Mặt đứng chính nhìn từ +Y nên đầu khuôn nằm bên trái, giống hình bóng ZE UT ở trang 9 catalogue.
6. **Thư viện Blender viết thành file `tools/ze_helpers.py`**, nạp bằng `exec` qua MCP, thay cho việc chỉ giữ trong `driver_namespace` như phiên GX200. Lý do: nhiều subagent nối tiếp nhau và Blender có thể khởi động lại.
   - Đã chạy thử trong scene `ze155`: box, cyl, tube, camera trực giao theo `views.json`, render Workbench, bbox.
   - Sửa một lỗi: `bound_box` của curve sai trong Blender 5.2, nên bbox tính từ evaluated mesh.
7. **Tổ chức subagent (Opus 5.5, cùng model với phiên):**
   - Phase 1 chạy song song: web researcher và PDF analyst.
   - Phase 2: designer làm `design.md`, `parts.json` và bộ bản vẽ, sau đó reviewer độc lập kiểm tra rồi sửa.
   - Phase 3: các builder chạy lần lượt (chỉ có một Blender), chia theo cụm: khung + truyền động, xi lanh + cấp liệu + hút chân không, đường chảy + T-die, hoàn thiện. Sau đó reviewer độc lập kiểm tra mô hình, rồi một vòng sửa.
8. **Trục làm nguội (chill roll)** không thuộc "máy" nhưng cần để thể hiện quy trình. Dựng ở mức đơn giản trong collection riêng `ze155_context`, và vẽ trên bản vẽ bằng nét gạch dài hai chấm (phantom).
9. **Thông số chuẩn là ZE 155 A UT theo bảng KM** (research web, `claims.jsonl`):
   - đường kính vít D = 169 mm, khoảng cách tâm hai trục khoảng 142 mm, D/d = 1,46;
   - 400 vòng/phút, 35 kNm mỗi trục;
   - tâm trục cao 1 200 mm so với sàn.
   - 34D = 5 746 mm, gồm 1 đoạn 4D (676 mm) và 5 đoạn 6D (1 014 mm). Quyết định này thay số 4 (D = 155 chỉ là tên gọi danh nghĩa).
   - Hình bóng trang 9 là hình mẫu dùng chung (ZE 180 bằng ZE 155 phóng ×1,05), nên chỉ lấy bố cục và tỷ lệ tương đối, không lấy tỷ lệ tuyệt đối 45,2 mm/pt.
   - Chọn bản A thay vì R: A là bản tiêu chuẩn, mô-men cao nhất. Bản R (D = 181) hợp hơn cho khử khí sâu. Designer được đổi sang R nếu có lý do rõ.
10. **Bố trí khuôn: T-die nằm ngang, cùng trục với đường chảy, môi khuôn chĩa vào khe giữa trục giữa và trục dưới của cụm 3 trục cán láng đứng.** Lấy theo sơ đồ dây chuyền trong catalogue trang 24–25 và tài liệu tấm PET của KM. Quyết định này thay số 8: không còn là chill roll đặt dưới khuôn.
    - Cụm cán láng dựng đơn giản trong `ze155_context`.
    - Năng suất thiết kế 3,5 t/h PET, tấm rộng 2,1 m, môi khuôn rộng 2,4 m (`specs.md` §0).
11. **Bốn điểm designer để ngỏ:**
    1. **Mối nối xi lanh dùng mặt bích bắt bu-lông, không dùng C-clamp.** Ưu tiên giống máy thật: ảnh ZE UT cỡ lớn cho thấy mặt bích (c037). C-clamp chỉ do brief của orchestrator tự liệt kê, người dùng không yêu cầu.
    2. **Giữ vỏ che dạng hộp (C1–C6)**, theo trang 9 và ảnh trang 16.
    3. **Giữ động cơ 1 500 kW cao khoảng 2,6 m** (khung AMI 450, có bộ làm mát trên nóc). Hình bóng trang 9 là hình mẫu dùng chung nên không đúng chiều cao.
    4. **Chấp nhận khe khí 200 mm** từ môi khuôn tới khe trục cán; giữ khuôn nằm ngang theo quyết định 10.
12. **Chạy song song để rút ngắn thời gian:**
    - drafter vẽ bản vẽ, reviewer độc lập review thiết kế, builder phase 1 dựng khung và truyền động.
    - Lý do: khung bệ và truyền động ít khả năng đổi sau review. Nếu review đổi phần đó, phase sau sẽ sửa.
    - Orchestrator không gọi Blender trong lúc có builder đang chạy, để không xung đột.
13. **Phân loại review thiết kế 01** (1 Critical, 8 Important, 11 Minor):
    - Sửa C1, I1–I8 và các Minor M1, M3–M10.
    - Hoãn M2 (cụm truyền động dài hơn khoảng 7 % so với bảng KM) và M11 (tủ cuối máy chưa khớp khối trang 9), vì builder phase 1 đang dựng đúng các bộ phận đó. Nếu sai thì phải chịu: truyền động dài hơn thật một chút, tủ cuối máy khác hình mẫu.
    - Designer báo lại danh sách bộ phận đổi bbox để drafter và các builder làm lại đúng phần đó.
14. **Builder phase 1 đã xong:** 72 object chi tiết, file lưu 252 object. Orchestrator tự xem `drive-persp-r2` và `drive-p19-r2-cmp`, thấy đạt.
    - Ghi lại cho vòng hoàn thiện: xanh KM đang quá bão hòa so với web-12 và p16, nên giảm độ bão hòa; vỏ hộp số còn vuông, cần thêm gân và bo cạnh kiểu gang đúc.
    - Phase 2 chờ designer áp xong review-01, vì I1, I4 và C1 rơi vào xi lanh, cấp liệu và chân không.
15. **Drafter đã xong:** 7 tờ bản vẽ và 12 hình chiếu, `verify_views` chạy 68 phép thử, không lỗi nào.
    - Orchestrator đã xem tờ 01 (bố trí chung, GA) và tờ 05 (T-die): đạt. Lỗi trình bày cần sửa: một đường dẫn chú thích trên tờ 05 chạy ra ngoài khung, vài đường dẫn chú thích cắt nhau.
    - Ba lỗi dữ liệu drafter báo (vị trí bu-lông thanh chặn, dầm sàn trùng lỗ ống cấp liệu, khung trục cán sát deckle) giao designer vá. Sau đó drafter vẽ lại.
16. **Builder phase 2 đã xong:** thêm 124 object, file có 417 object, 695 nghìn tam giác. Orchestrator đã xem `p2-p16-r2-cmp` và `p2-web02-r2-cmp`: hình khối và chi tiết đạt.
    - So với web-02 vẫn thiếu mật độ: nhiều cáp và ống mềm hơn, vành đục lỗ của vỏ gia nhiệt, dàn van nước dày hơn.
    - Để phase 4 tăng mật độ chi tiết ở những chỗ nhìn thấy nhiều nhất: dàn nước phía +Y, cáp gia nhiệt.
    - Vòm hút chân không giữ dạng hộp theo thiết kế; ảnh p01 có vòm tròn nhưng đó là máy UTX nhỏ.
17. **Phân loại review bản vẽ 01** (2 Critical, 10 Important, 8 Minor): sửa toàn bộ Critical và Important.
    - Designer sửa phần dữ liệu:
      - I2: liên động, nguồn cấp vào, nút dừng khẩn ở khuôn và đường chảy;
      - I3: P3 điều khiển tốc độ bơm bánh răng;
      - I4: bu-lông thân khuôn;
      - I5: rãnh bản lề môi khuôn mở;
      - I6: mặt bích xi lanh tăng từ Ø600 lên Ø640, chỗ khoét trên vỏ che tăng lên Ø660.
    - Sau đó drafter vẽ lại và sửa phần vẽ:
      - C1: lỗ Ø100 vào khuôn;
      - C2: thông số mặt bích lấy theo dữ liệu, thêm mặt cắt mặt bích;
      - I1: mạch nước xi lanh;
      - I7: chi tiết khớp nối và trục then hoa;
      - I8: tuyến cáp, khí, tín hiệu;
      - I9: tăng cỡ chữ lên ≥ 2,5 mm;
      - I10: tờ 07 chuyển sang dạng P&ID có ký hiệu.
    - Builder phase 3 được báo ngay về bu-lông thân khuôn, rãnh bản lề và nút dừng khẩn, vì đang dựng khuôn.
    - Mặt bích Ø640 (I6) thuộc phần đã dựng ở phase 2, giao phase 4 sửa: phóng mặt bích, mở rộng chỗ khoét trên vỏ che.
18. **Giữ thân khuôn sâu 450 mm**, không làm sâu tới X 9060 như designer đề xuất (design.md §9 mục 6).
    - Lý do: khuôn đang được dựng ở phase 3. Nhìn từ ngoài, khuôn sâu 450 hay 600 mm khác rất ít.
    - Nếu sai thì phải chịu: thành thân khuôn quanh ống phân phối và thanh chặn mỏng hơn thực tế; chỉ thấy được khi đọc mặt cắt A–A.
19. **Phân vai theo yêu cầu người dùng:** designer, drafter, builder, reviewer và fixer là các agent riêng. Reviewer không sửa; agent làm ra sản phẩm không tự nghiệm thu bản cuối. Agent nào dài quá thì viết file bàn giao gọn và giao cho agent mới. Hiện đã có:
    - `drawings/HANDOVER.md` (drafter cũ, khoảng 813k token, nghỉ);
    - `design/HANDOVER.md` (designer cũ, khoảng 750k token, nghỉ sau khi viết file bàn giao).
20. **Đảo quyết định 18:** drafter phát hiện hàng bu-lông thân khuôn đi xuyên qua ống phân phối khi thân khuôn chỉ sâu 450 mm.
    - Lùi mặt sau khuôn khoảng 66 mm, tới X ≈ 9060, rồi đặt lại các hàng bu-lông cho tránh ống phân phối.
    - Thay đổi kéo theo: ống nối vào khuôn ngắn lại, hộp gia nhiệt dời theo.
    - Designer mới làm phần dữ liệu, drafter mới vẽ lại, builder sửa khuôn trong Blender.
21. **Giảm độ hoàn hảo theo người dùng ("không cần quá hoàn hảo"). Đóng băng thiết kế: `design/parts.json` lúc 23:14 là bản cuối.**
    - Dừng designer 2 giữa chừng. Quyết định 20 bị hủy: không làm khuôn sâu thêm. Hàng bu-lông đi qua ống phân phối được giữ như một đơn giản hóa đã biết; chỉ thấy trong mặt cắt, mô hình nhìn từ ngoài không đổi.
    - `build_parts.py` đang dở phần sửa khuôn nên được đổi tên thành `build_parts.partial_die_edit.py`, không ai được chạy lại.
    - Từ đây chỉ sửa những gì nhìn thấy được trên mô hình và bản vẽ. Không còn vòng review bản vẽ thứ hai.
    - Còn lại: builder 4a, drafter 2 làm gọn, builder 4b hoàn thiện ngoại quan, render và báo cáo, một reviewer độc lập cho mô hình, một vòng sửa chỉ cho lỗi nhìn thấy được.
22. **Bộ bản vẽ chốt ở bản sửa B:** 9 tờ, `verify_views` 68 phép thử không lỗi, không chữ chồng, không có gì ra ngoài khung.
    - Giữ tờ 08, tờ 09 và các đường ngắt hình vì đã làm xong trước khi giảm phạm vi.
    - Không chạy vòng review bản vẽ thứ hai (quyết định 21). Bản vẽ sẽ được reviewer mô hình xem lướt khi đối chiếu ở cuối.
23. **Builder 4a đã xong:** đủ 187/187 bộ phận, 579 object, khoảng 1,19 triệu tam giác. Đã sửa 47 object bị gán sai vật liệu, mặt bích tăng lên Ø640, kiểm 72/72 mối nối.
    - Builder 4b hoàn thiện ngoại quan: chất lượng EEVEE, nền và ánh sáng, màu xanh KM, chrome và tấm PET, dáng gang đúc của hộp số, mật độ cáp. Sau đó render, ghép ảnh so sánh và viết `report.md`.
    - Tiếp theo: một reviewer độc lập chỉ xem mô hình, rồi một agent sửa riêng chỉ sửa lỗi nhìn thấy được.
24. **Builder 4b đã xong:** 11 ảnh render cuối, 8 ảnh so sánh, file 602 object, khoảng 1,22 triệu tam giác, bbox 18 220 × 7 900 × 6 309 mm. Orchestrator đã xem `ze155-hero` và `ze155-die-rolls`: đạt.
    - Subagent báo harness không cho subagent ghi file `report.md`. Orchestrator sẽ tự viết `out/report.md` ở bước cuối, lấy nội dung subagent gửi làm nháp: kiểm lại số liệu, sửa chỗ sai (designer 2 bị dừng chứ không "làm gọn") và thêm kết quả review cuối.
    - Reviewer mô hình độc lập chỉ ghi lỗi; một agent sửa riêng (builder 4c) xử lý Critical và Important nhìn thấy được.
25. **Review mô hình 01:** 1 Critical, 6 Important, 5 Minor; khớp bản vẽ, không chi tiết nào lơ lửng.
    - Builder 4c (agent sửa riêng) sửa:
      - C1: tấm PET và crôm;
      - I1: tấm PET chạy ra khỏi giá, có con lăn và băng tải ngắn;
      - I2: hai ống khí cụt;
      - I3: kính thăm;
      - I4: điểm đầu cáp;
      - I5: ống nước xuyên cột;
      - I6: z-fighting logo;
      - các Minor rẻ.
    - Không review vòng hai (quyết định 21). Orchestrator tự xem các ảnh render lại để nghiệm thu.
26. **Kết thúc:**
    - Builder 4c sửa 11/12 lỗi; orchestrator nghiệm thu bằng hero và die-end34.
    - Đã kiểm trong Blender: scene `Scene` vẫn đúng 3 object (Camera, Cube, Light); file đang mở chưa bao giờ được lưu.
    - `out/ze155.blend` có 610 object.
    - Orchestrator viết `out/report.md`.
27. **Animation và mặt cắt (2026-10-05):**
    - Người dùng yêu cầu animation và mặt cắt để kiểm công nghệ lõi: trục quy trình từ hạt tới tấm, bên trong máy, tương tác cả cụm.
    - Agent thiết kế anim lập `anim/` (brief, `shots.json`, `interior_parts.json`, storyboard). Reviewer độc lập (`anim/review-anim-01.md`): 1 Critical, 9 Important, 11 Minor. Agent thiết kế đã sửa đủ 21 lỗi. Không chạy review vòng hai; orchestrator xem lại brief và contact sheet.
    - Người dùng đã duyệt: D1, dựng trong scene mới `ze155_anim`; D2, dọn camera là một bước của animation.
    - Chờ người dùng trả lời Q1–Q7 trước khi dựng. Blender đang mở `out/ze155.blend` (có thay đổi chưa lưu, không phải do agent).
28. **Duyệt dựng animation (2026-10-05):**
    - Người dùng: "làm như bình thường". Không cho Blender nền (Q7 = không), không dựng song song trong Blender.
    - Q1–Q6 theo đề xuất trong brief: bản đủ 3:31; giữ khuôn 450 mm với rãnh gần chữ T; nhãn làm hậu kỳ; badge tốc độ; lệch design chỉ sửa trong anim; vòng điều khiển kiểu dây chuyền tấm (a).
    - Giữ nguyên các thay đổi chưa lưu trong phiên đang mở (người dùng không yêu cầu revert).
    - Thứ tự: C0 → A1 → A2 → A3, mỗi phase một agent, chạy qua MCP. Song song chỉ có một agent hậu kỳ không dùng Blender. Sau A3: reviewer độc lập, rồi fixer riêng, rồi render qua MCP theo đợt.
    - Hướng dẫn chung cho builder: `anim/BUILD-ANIM.md`.
29. **Đổi đích: web React Three Fiber (2026-10-05):**
    - Người dùng: đích cuối là web R3F, không phải MP4. Brief trước giả định phim vì orchestrator không hỏi lại đích khi người dùng hỏi về GLB/R3F.
    - Huỷ render 5 275 khung và ghép MP4. Pipeline Pillow trong `anim/post/` chỉ còn để tham khảo bố cục HUD.
    - Giữ hình học bên trong (A1a, A1b), bản cắt sẵn, nhóm `ax_*` và `shots.json` (dùng làm kịch bản tour).
    - Phần R3F gắn vào dự án R3F có sẵn của người dùng; đang chờ đường dẫn. Tìm trên máy không thấy package.json nào dùng three/R3F.
    - A2 theo hướng Blender (driver, particle, shader) không làm; thay bằng bước chuẩn bị cho web cộng code R3F.
30. **Chọn phương án C cho web (2026-10-05):**
    - Người dùng chọn C: xuất GLB bằng tiến trình Blender nền `blender -b --factory-startup out/ze155_anim.blend --python ...`.
    - Ngoại lệ BRIEF (cấm Blender nền) chỉ cho việc xuất. Tiến trình nền chỉ đọc file `.blend` đã lưu, không bao giờ lưu, chỉ ghi vào `web/build/`.
    - Không đụng Blender người dùng đang mở, không dùng MCP để xuất. Bỏ Q6 (sao lưu phiên).
    - Cấu trúc (thiết bị, pivot, trạng thái cắt, clip) nằm trong JSON và được dựng lúc chạy trong R3F. Không dựng lại cây trong Blender.
    - Q2–Q5 theo đề xuất: mặt cắt kết hợp, chọn theo thiết bị, phạm vi bản đầu như Q4, bộ công cụ React 19.3 / R3F 9.8.1 / drei 10.7.9 / three 0.186.1 / Vite 8.
    - Người dùng yêu cầu lập kế hoạch chi tiết cho Đợt 1 trước khi làm.
31. **Bắt đầu dựng Đợt 1 (2026-10-05):**
    - Người dùng: "Làm đi". Kế hoạch: `web/PLAN-DOT1.md` cộng `web/dot1/AMENDMENTS.md` (sửa I1, I2, các lỗi Minor, cắt phạm vi theo M2; Đợt 1b để sau).
    - Hai builder chạy song song: A (xuất, nén, dữ liệu, kiểm GLB, cây thiết bị, bảng thông tin, thanh công cụ) và B (sandbox `web/web-check`).
    - Xong mốc 1a cho người dùng xem trước. Xong Đợt 1 thì soát độc lập trên Chrome, rồi fixer riêng sửa.
32. **Tạm dừng Đợt 3 (2026-10-05):**
    - Người dùng: "Khoan làm đợt 3". Tour, nhãn, HUD, sơ đồ khối chưa làm cho tới khi người dùng cho phép.
    - Đợt 1 vẫn soát và sửa như kế hoạch. Đợt 2 làm theo quy trình gọn: brief ngắn → soát nhanh → dựng → soát trên Chrome → sửa.
