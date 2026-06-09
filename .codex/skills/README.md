# 🧭 Danh Sách Kỹ Năng Của Agent (Codex Skills Library)

Thư mục này chứa các kỹ năng cục bộ (Agent Skills) dành cho các Agent phát triển dự án **PhoneGuard AIoT**.

---

## 🗺️ Bản Đồ Kỹ Năng

* **`phoneguard-rules`**: Kỹ năng bắt buộc sử dụng trong toàn bộ dự án. Cấu hình quy chuẩn ngôn ngữ tiếng Việt cho trao đổi và comment, yêu cầu log debug, tối ưu hóa dữ liệu real-time và quy định tự động commit/push Git.
  - Vị trí: `.codex/skills/phoneguard-rules/SKILL.md`

---

## 🧭 Hướng Dẫn Kích Hoạt Kỹ Năng
Các Agent khi khởi chạy sẽ quét thư mục này để hiểu các quy định đặc thù của dự án. Nếu bạn sử dụng dòng lệnh CLI để thêm kỹ năng, có thể chạy:

```bash
npx skills add https://github.com/Phuc-Bang/phoneguard-aiot --skill "phoneguard-rules"
```
