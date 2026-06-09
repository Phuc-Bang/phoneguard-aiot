# PhoneGuard AIoT Frontend

Dashboard React + Vite + TypeScript cho PhoneGuard AIoT.

## Tech stack

- React
- Vite
- TypeScript
- TailwindCSS
- Recharts
- Lucide React Icons

## Chạy local

```bash
cd frontend
npm install
npm run dev
```

Mở:

```text
http://localhost:5173
```

## API base URL

Frontend đọc API base URL từ:

```text
VITE_API_BASE_URL
```

Nếu không có biến môi trường, fallback:

```text
http://localhost:8000
```

Trong giao diện, vào **Settings** để đổi API base URL runtime. Giá trị này được lưu trong `localStorage`.

## API đang gọi

- `GET /health`
- `GET /latest`
- `GET /history`
- `GET /events`
- `POST /forecast`
- `POST /predict-risk`

Dashboard tự động refresh mỗi 3 giây.
