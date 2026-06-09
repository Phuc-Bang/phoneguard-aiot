---
name: phoneguard-rules
description: Quy chuẩn bắt buộc về lập trình, chú thích tiếng Việt, ghi log debug và tự động đẩy Git của PhoneGuard AIoT.
---

# Kỹ Năng Agent: Quy chuẩn phát triển PhoneGuard AIoT

Bộ kỹ năng này áp dụng các quy chuẩn phát triển nghiêm ngặt cho dự án PhoneGuard AIoT. Mọi AI Agent khi lập trình trong dự án này phải tuân thủ tuyệt đối các quy định dưới đây.

---

## 🌐 1. Quy Định Ngôn Ngữ & Chú Thích (Vietnamese Language Policy)
* **Ngôn ngữ phản hồi**: Luôn phản hồi người dùng bằng **Tiếng Việt**.
* **Chú thích mã nguồn (Comments)**: 
  - Mọi tệp tin mới tạo hoặc chỉnh sửa phải có phần comment header mô tả mục đích sử dụng.
  - Các hàm, lớp và đoạn code logic phức tạp phải được chú thích chi tiết bằng **Tiếng Việt có dấu**.
  - Ví dụ chú thích chuẩn:
    ```python
    # Khởi tạo kết nối đến SQLite Database sử dụng SQLAlchemy Engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    ```

---

## 🛠️ 2. Quy Định Logs & Debug (Debugging & Logs Policy)
* **Log Everything (Ghi log mọi sự kiện)**: Code phải đi kèm log debug rõ ràng.
* **Backend (Python)**:
  - In log khi nhận được HTTP POST từ client (ví dụ: `print(f"[DEBUG] Nhan telemetry tu device: {device_id} - Pin: {level}%")`).
  - Ghi log khi phân tích AI phát hiện dị thường hoặc sinh khuyến nghị mới.
  - Ghi log khi phát sóng WebSocket.
* **Frontend (Javascript)**:
  - Ghi log khi mở hoặc đóng kết nối WebSocket (`console.log("[DEBUG] WebSocket opened")`).
  - Ghi log khi nhận dữ liệu từ server và khi bắt đầu cập nhật dữ liệu lên biểu đồ Chart.js.

---

## 🎨 3. Quy Định Thiết Kế (UI/UX Taste System)
* Áp dụng nguyên lý **Bento Grid 12 cột** và **Double-Bezel Card Layout** theo đúng hướng dẫn tại [docs/design_system_and_skills.md](file:///e:/AIoT/Home-Work/phoneguard-aiot/docs/design_system_and_skills.md).
* **Khóa màu neon**: Chỉ sử dụng đúng mã màu neon quy định cho các trạng thái pin, nhiệt độ, sạc và gia tốc. Không sử dụng các gradient tím loãng rập khuôn (AI slop).
* **Tactile Feedback**: Đảm bảo tất cả các nút tương tác và card đều có phản ứng bấm vật lý nhẹ thông qua hiệu ứng `:active` co giãn `scale-[0.99]`.

---

## 🚀 4. Quy Trình Tự Động Hóa Git (Git Push Policy)
Ngay khi hoàn thành một tệp code hoặc kết thúc một tác vụ, Agent phải tự động thực thi các lệnh:
1. **Kiểm tra trạng thái**: `git status`
2. **Add & Commit**:
   ```bash
   git add .
   git commit -m "feat/fix: <mô tả chi tiết bằng Tiếng Việt có dấu>"
   ```
3. **Push lên Repo**:
   ```bash
   git push origin main
   ```
   *(Địa chỉ Repo: `https://github.com/Phuc-Bang/phoneguard-aiot.git`)*

---

## 📁 5. Loại Trừ Thư Mục CodeGraph (Exclusions)
* **Tuyệt đối không đụng vào `.codegraph/`**: Không được đọc, sửa đổi, xóa hoặc commit các tệp tin trong thư mục `.codegraph/`. Đây là cơ sở dữ liệu phân tích mã nguồn cục bộ sinh ra bởi CodeGraph daemon và cần được loại trừ hoàn toàn khỏi mọi hoạt động của AI Agent.
