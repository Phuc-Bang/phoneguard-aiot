---
name: phoneguard-aiot-rules
description: Các quy tắc bắt buộc dành cho AI Agent khi phát triển và bảo trì dự án PhoneGuard AIoT.
---

# PhoneGuard AIoT - Developer Agent Guidelines

Tài liệu này chứa các quy định bắt buộc đối với bất kỳ AI Coding Agent nào (Antigravity, Codex, Cursor, Claude Code,...) khi tham gia lập trình, sửa lỗi hoặc mở rộng dự án **PhoneGuard AIoT**.

---

## 🌐 1. QUY ĐỊNH VỀ NGÔN NGỮ & GIAO TIẾP (Language Rules)
* **Giao tiếp với người dùng**: Luôn trao đổi và báo cáo bằng **Tiếng Việt**.
* **Giải thích mã nguồn (Comments)**: Mọi ghi chú giải thích thuật toán, luồng dữ liệu bên trong code (Python, JS, HTML, CSS) phải viết bằng **Tiếng Việt có dấu** rõ ràng, chi tiết, dễ hiểu.

---

## 🛠️ 2. QUY ĐỊNH VIẾT CODE & DEBUG (Logging & Debugging Rules)
* **Luôn viết kèm log debug**: Khi viết các hàm xử lý API, xử lý WebSocket, hoặc tính toán logic AI, phải tích hợp đầy đủ các log ghi nhận tiến trình:
  - **Python (Backend)**: Sử dụng module `logging` (ví dụ: `logger.debug`, `logger.error`) hoặc `print("[DEBUG] ...")` tại các điểm mấu chốt (khi nhận dữ liệu, bắt đầu phân tích AI, lỗi kết nối DB, hoặc gửi WebSocket).
  - **Javascript (Frontend)**: Sử dụng `console.log("[DEBUG] ...")` hoặc `console.error` khi kết nối/mất kết nối socket, nhận telemetry mới, cập nhật biểu đồ.
* **Mục tiêu**: Giúp nhà phát triển dễ dàng theo dõi dòng dữ liệu và khắc phục sự cố tức thì.

---

## 🎨 3. QUY CHUẨN THIẾT KẾ (UI/UX Taste System)
* Đọc và tuân thủ tuyệt đối các quy định thiết kế Bento Grid và Double-Bezel Card Layout trong tài liệu:
  👉 [docs/design_system_and_skills.md](file:///e:/AIoT/Home-Work/phoneguard-aiot/docs/design_system_and_skills.md)
* Khóa bảng màu neon theo trạng thái, không được tự ý sinh các gradient màu tím rác mắt (AI-purple slop).

---

## 🚀 4. QUY TRÌNH HOÀN THÀNH & ĐẨY LÊN GIT (Git Commit & Push Rules)
Mỗi khi hoàn thành một tính năng, sửa xong một lỗi, hoặc cập nhật tài liệu:
1. **Kiểm tra trạng thái Git**: Chạy `git status` để xem các file thay đổi.
2. **Tạo Commit**: Commit code với thông điệp rõ ràng bằng Tiếng Việt (hoặc Tiếng Anh chuẩn) mô tả đúng việc đã làm.
   - Ví dụ: `git commit -m "feat: cập nhật logic phát hiện dị thường nhiệt độ và thêm debug log"`
3. **Đẩy lên Repository**: Tự động thực hiện lệnh push lên GitHub của dự án:
   ```bash
   git push origin main
   ```
   *(Đường dẫn kho lưu trữ: `https://github.com/Phuc-Bang/phoneguard-aiot.git`)*
