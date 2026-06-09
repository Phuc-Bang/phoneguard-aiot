# 🧠 Hướng Dẫn Dành Cho AI Agent (Lập Trình Viên)

Tài liệu này xác định vai trò, kiến trúc hệ thống và các quy định bắt buộc đối với các Agent AI (như Codex, Cursor, Claude Code, Gemini, Antigravity,...) khi phát triển và bảo trì dự án **PhoneGuard AIoT**.

---

## 📁 1. Bản Đồ Tài Liệu & Cấu Trúc Dự Án (Documentation Map)

Cấu trúc thư mục của dự án **PhoneGuard AIoT** được tổ chức như sau:

```text
phoneguard-aiot/
├── .docs/                             <-- Thư mục chứa chỉ dẫn lõi của Agent (được đẩy lên Git)
│   ├── AGENTS.md                      <-- 🧠 Bộ não dự án (Quy định vai trò, Techstack, Bản đồ tài liệu)
│   └── WORKFLOW.md                    <-- 🔄 Quy trình chuẩn sửa lỗi & phát triển tính năng
│
├── skills/                            <-- 🧭 Kỹ năng dự án (Quy định viết code, tiếng Việt, log debug, và đẩy Git)
│   └── phoneguard-rules/
│       └── SKILL.md                   <-- 📏 Nội dung kỹ năng (cả Agent cục bộ và CLI đều quét ở đây)
│
├── .codegraph/                        <-- Cơ sở dữ liệu phân tích đồ thị mã nguồn (CodeGraph Index)
│
├── backend/                           <-- 🐍 FastAPI Backend & AI logic
│   ├── app/
│   │   ├── ai/                        <-- Các module AI (Phát hiện dị thường, dự báo pin)
│   │   ├── database.py                <-- Cấu hình kết nối SQLite
│   │   ├── models.py                  <-- SQLAlchemy models
│   │   ├── schemas.py                 <-- Pydantic schemas
│   │   ├── crud.py                    <-- Thao tác đọc/ghi cơ sở dữ liệu
│   │   └── main.py                    <-- FastAPI entrypoint & WebSocket
│   ├── requirements.txt               <-- Thư viện backend cần thiết
│   └── Dockerfile                     <-- Containerization backend
│
├── frontend/                          <-- 🎨 Dashboard Web (Glassmorphism Bento)
│   ├── index.html                     <-- Giao diện HTML5 chuẩn SEO
│   ├── css/
│   │   └── style.css                  <-- CSS Glassmorphic cao cấp
│   └── js/
│       └── app.js                     <-- WebSocket & Chart.js cập nhật real-time
│
├── docs/                              <-- 📖 Tài liệu công khai của dự án
│   └── design_system_and_skills.md    <-- Quy chuẩn thiết kế UI/UX theo Taste Skill
│
├── scripts/                           <-- ⚙️ Các script bổ trợ
│   ├── phone_simulator.py             <-- Script giả lập gửi dữ liệu điện thoại
│   └── train_models.py                <-- Huấn luyện mô hình Isolation Forest ban đầu
│
├── docker-compose.yml                 <-- File điều phối container (port 8005)
├── .gitignore                         <-- File cấu hình loại trừ của Git
└── README.md                          <-- Hướng dẫn chạy dự án tổng quan
```

---

## 🛠️ 2. Quy Định Vai Trò Lõi Của Agent (Role & Constraints)

Khi thực hiện bất kỳ nhiệm vụ nào trong repository này, Agent **phải tuân thủ**:

1. **Giao Tiếp Bằng Tiếng Việt**: Luôn trao đổi với người dùng bằng **Tiếng Việt**.
2. **Comment Tiếng Việt Có Dấu**: Tất cả các đoạn comment giải thích mã nguồn trong các file code (Python, JS, HTML, CSS) phải viết bằng **Tiếng Việt có dấu**, diễn giải chi tiết mục đích, luồng xử lý và kết quả của hàm/biến đó.
3. **Luôn Bổ Sung Log Debug**:
   - Trong code Python backend: Sử dụng `logger.debug` hoặc `print("[DEBUG] ...")` tại các luồng API nhận dữ liệu cảm biến, lưu cơ sở dữ liệu, phát hiện dị thường và WebSocket.
   - Trong code Javascript frontend: Sử dụng `console.log("[DEBUG] ...")` để in dữ liệu nhận được từ WebSocket và trạng thái cập nhật UI.
4. **Quy Trình Git Tự Động**: Mỗi khi viết xong một tính năng hoặc sửa lỗi, phải tự động chạy lệnh kiểm tra `git status`, tạo commit rõ ràng và `git push` trực tiếp lên nhánh `main` của repo: `https://github.com/Phuc-Bang/phoneguard-aiot.git`.
5. **Định Dạng Giao Diện**: Luôn tuân thủ quy định Bento Grid, viền kép Double-Bezel và khóa màu neon trong [design_system_and_skills.md](file:///e:/AIoT/Home-Work/phoneguard-aiot/docs/design_system_and_skills.md).
6. **Loại trừ cơ sở dữ liệu CodeGraph**: Tuyệt đối không bao giờ đọc, chỉnh sửa, xóa hoặc commit các tệp tin trong thư mục `.codegraph/`. Đây là cơ sở dữ liệu phân tích mã nguồn cục bộ và cần được loại trừ hoàn toàn khỏi mọi hoạt động của AI Agent.

---

## 📊 3. Danh Sách Kỹ Năng Cần Load (Codex Skills compliance)
Trước khi bắt đầu nhiệm vụ, hãy đọc và áp dụng kỹ năng tại:
👉 `skills/phoneguard-rules/SKILL.md` (chứa các hướng dẫn kỹ thuật chi tiết về coding, debugging và git).
