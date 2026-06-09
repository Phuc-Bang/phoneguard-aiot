# 🎨 PhoneGuard AIoT - Design System & Anti-Slop Guidelines (Taste Skill Application)

Tài liệu này áp dụng triết lý thiết kế giao diện cao cấp từ **Taste Skill** (ngăn chặn các thiết kế AI rập khuôn - "AI slop") vào hệ thống **PhoneGuard AIoT Dashboard**. Đây là cẩm nang hướng dẫn duy trì tính thẩm mỹ, hiệu năng và quy chuẩn code cho cả phần Frontend và Backend của dự án.

---

## 📌 0. DESIGN READ & THE THREE DIALS (Thiết lập cấu hình lõi)

### Design Read (Đọc vị Thiết kế)
> **"Reading this as: Monitoring Dashboard (Cockpit) for AIoT device owner/developer, with a dark tech / premium glassmorphism language, leaning toward custom CSS Grid layout + Chart.js dynamic rendering + strict real-time density."**

### Dial Configurations (Cấu hình Dials)
* **`DESIGN_VARIANCE: 5`** *(Trung bình - Cân bằng)*: Dashboard cần sự đối xứng, gọn gàng để dễ theo dõi các số liệu kỹ thuật, tránh bố cục lộn xộn.
* **`MOTION_INTENSITY: 7`** *(Khá cao - Mượt mà)*: Đòi hỏi chuyển động thời gian thực từ cảm biến (Gia tốc, Pin) phản hồi tức thì và mượt mà, nhưng không được lạm dụng các hiệu ứng chuyển động lặp vô hạn.
* **`VISUAL_DENSITY: 8`** *(Cao - Dày đặc thông tin)*: Đây là một màn hình giám sát (Cockpit), do đó dữ liệu cần hiển thị cô đọng, nhiều thông tin và biểu đồ trực quan thay vì quá nhiều khoảng trắng trống trải.

---

## 🛠️ 1. HỆ THỐNG MÀU SẮC NEON (Color Calibration)

Dự án áp dụng quy tắc **khóa tính nhất quán màu sắc** (Color Consistency Lock). Toàn bộ trang web chỉ sử dụng các tone màu trung tính sẫm làm nền và **tối đa 1 màu nhấn chính (Electric Cyan)** cho thông tin chung. Các màu khác được ánh xạ nghiêm ngặt theo trạng thái hoạt động:

| Trạng thái / Chỉ số | Màu sắc chủ đạo | Mã màu HEX | Ứng dụng thực tế |
| :--- | :--- | :--- | :--- |
| **Nền chính (Neutral)** | Space Navy / Slate | `#07090e` / `#0f131f` | Nền trang web và các thẻ card kính mờ |
| **Chỉ số chung (Primary)** | Electric Cyan | `#00f0ff` | Trạng thái kết nối WebSocket, biểu đồ đường gia tốc X |
| **Sức khỏe tốt / Đang sạc** | Neon Green | `#39ff14` | Đèn sạc pin, mức pin đầy, trạng thái sức khỏe tốt |
| **Cảnh báo (Warning)** | Neon Amber | `#ffaa00` | Pin ấm (>40°C), biểu đồ đường gia tốc Y, cảnh báo mức trung bình |
| **Nguy hiểm (Critical)** | Neon Red-Rose | `#ff0055` | Rơi tự do (Free fall), va chạm mạnh, pin quá nhiệt (>45°C), biểu đồ Z |

> [!CAUTION]
> **Cấm tuyệt đối:** Tự ý thêm các hiệu ứng phát sáng nút màu tím (AI-purple slop) hoặc thay đổi tone màu grays đột ngột giữa các phân vùng trên giao diện.

---

## ✍️ 2. QUY CHUẨN TYPOGRAPHY (Typography System)

* **Headline / Số liệu chính**: Sử dụng font **Outfit** với tracking hẹp (`tracking-tight` / `tracking-tighter`) để tạo cảm giác kỹ thuật, sắc nét và hiện đại.
* **Body / Cảnh báo / Khuyến nghị**: Sử dụng font **Inter** (`leading-relaxed`) giúp tối ưu khả năng đọc các đoạn text dài.
* **Thông số vector (Gia tốc, tín hiệu mạng)**: Sử dụng font monospace (được kế thừa qua CSS hoặc `font-family: monospace`) để các số liên tục nhảy không làm thay đổi kích thước thẻ (layout shift).
* **Quy tắc Descender khi dùng Italic**: Khi hiển thị chữ nghiêng ở màn hình hiển thị lớn, luôn cài đặt `leading-[1.1]` trở lên để tránh cắt mất phần đuôi của các chữ cái như `g, j, p, q, y`.

---

## 📐 3. BỐ CỤC KHÔNG RẬP KHUÔN (Layout & Density Discipline)

* **Viewport Stability (Độ ổn định khung hình)**: Không sử dụng chiều cao cố định dạng `h-screen`. Luôn sử dụng `min-h-[100dvh]` để tránh hiện tượng giao diện bị nhảy giật trên các trình duyệt di động (như Safari iOS khi thanh địa chỉ ẩn/hiện).
* **Grid over Flex-Math**: Sử dụng CSS Grid cho Dashboard thay vì Flexbox thủ công. Grid giúp cấu trúc 2 cột hoặc 4 cột tự động co giãn cực kỳ chuẩn xác trên desktop và điện thoại:
  ```css
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }
  ```
* **Bento Cell Count (Quy tắc Bento)**: Số lượng thẻ trên dashboard phải vừa khít với lượng thông tin. Hiện tại, layout có đúng 8 thẻ chức năng chính sắp xếp cân đối. Không chèn các thẻ trống hoặc "fake screenshots" bằng div.

---

## 🔄 4. TỐI ƯU HÓA HIỆU NĂNG REAL-TIME (Performance & Motion)

Khi xử lý luồng dữ liệu cảm biến tần suất cao (đặc biệt là Accelerometer 10-50Hz):
1. **Tránh re-render React liên tục**: Không sử dụng state (`useState` của React) để lưu trữ tọa độ gia tốc thô nếu không cần thiết. Thay vào đó cập nhật trực tiếp vào DOM (`innerText`) hoặc cập nhật mảng dữ liệu của Chart.js.
2. **Chart Update Optimization**: Khi vẽ biểu đồ gia tốc thời gian thực, tắt hiệu ứng chuyển động animation của Chart.js:
   ```javascript
   accelChart.update('none'); // Cập nhật mượt mà không block thread
   ```
3. **Capping History**: Giới hạn số lượng điểm biểu diễn trên biểu đồ (`maxHistoryPoints: 30-40`) để tránh rò rỉ bộ nhớ khi mở dashboard thời gian dài.

---

## 🚨 5. QUY TRÌNH KIỂM TRA TRƯỚC KHI BÀN GIAO (Pre-flight Checklist)

Trước khi đóng gói mã nguồn giao diện, hãy tự động đối chiếu các điểm sau:
- `[ ]` **Button Contrast**: Tất cả các nhãn button/badge phải có độ tương phản tối thiểu WCAG AA (đặc biệt là badge cảnh báo màu đỏ/vàng trên nền tối).
- `[ ]` **Single-line Nav**: Thanh tiêu đề điều hướng phải hiển thị trên một dòng duy nhất ở màn hình desktop, không bị trôi hay wrap thành 2 dòng.
- `[ ]` **No Emoji**: Không sử dụng emoji trong các nhãn giao diện hoặc thông số kỹ thuật (thay thế bằng các icon Vector từ FontAwesome/Phosphor).
- `[ ]` **Tactile Feedback**: Mọi hành vi tương tác nhấp nút phải có phản hồi vật lý nhẹ (ví dụ `:active` co tỷ lệ `scale-[0.98]`).
