# ZE 155 — trình xem dây chuyền 3D

Trình xem web dùng Vite, React và React Three Fiber: chọn thiết bị, focus, xem các mặt cắt cố định và mặt cắt tự do.

## Deploy Vercel

Import repository từ GitHub và dùng các thiết lập sau:

| Thiết lập | Giá trị |
| --- | --- |
| Framework Preset | Vite |
| Root Directory | `web/web-check` |
| Node.js Version | `22.x` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Không cần biến môi trường cho phiên bản hiện tại. Model và dữ liệu đã có trong `web/web-check/public`; Vercel build trực tiếp từ các asset này, không cần Blender.

## Chạy local

```bash
cd web/web-check
npm ci
npm run dev
```

Mở `http://localhost:5178/`.

## Nguồn và dữ liệu

- [Hướng dẫn app](web/web-check/README.md)
- [Plan Đợt 1](web/PLAN-DOT1.md)
- [Review focus và X4120](web/review/dot1/codex-fix-02/review.md)
- `web/tools/`: công cụ export, sinh và kiểm tra dữ liệu.
- `web/web-check/public/models/` và `public/data/`: asset được đưa lên website. Khi cập nhật dữ liệu, sửa nguồn chuẩn và publish bằng pipeline trong `web/Makefile`.

Các thư mục build/cache, file Blender, video, archive và ảnh render cũ được bỏ qua bởi `.gitignore`. Nguồn script, cấu hình, dữ liệu app và bằng chứng review hiện tại được giữ trong Git.
