# 07. Phân Tích Rủi Ro Và Cơ Chế An Toàn

## Rủi ro khi AI sai

PhoneGuard AIoT dùng AI/rule-based để hỗ trợ quan sát thiết bị, nhưng kết quả có thể sai vì nhiều nguyên nhân.

| Rủi ro | Nguyên nhân | Hậu quả |
|---|---|---|
| False positive anomaly | Cảm biến nhiễu, điện thoại rung mạnh nhưng không rơi | Người dùng nhận cảnh báo không cần thiết |
| False negative anomaly | Cảm biến thiếu dữ liệu hoặc browser không cấp quyền | Hệ thống bỏ sót sự kiện bất thường |
| Forecast sai | Dữ liệu quá ít, pin giảm không tuyến tính, điện thoại vừa cắm/rút sạc | Dự báo pin 15/30 phút không chính xác |
| Risk recommendation sai | Anomaly và forecast đều có confidence thấp | Khuyến nghị chưa phù hợp với tình huống thực tế |
| Mất kết nối mạng | Redmi và laptop không cùng Wi-Fi, backend URL sai | Telemetry không đến backend |

## Cơ chế an toàn bắt buộc

### 1. AI không tự điều khiển thiết bị

PhoneGuard AIoT chỉ đưa ra cảnh báo và khuyến nghị. Hệ thống không tự tắt ứng dụng, không tự thay đổi cấu hình điện thoại, không tự điều khiển sạc hoặc mạng.

### 2. Anomaly cao chỉ cảnh báo

Khi `severity = HIGH` hoặc `CRITICAL`, backend chỉ ghi event và dashboard hiển thị cảnh báo. Người dùng vẫn là người quyết định hành động tiếp theo.

Ví dụ:

- `POSSIBLE_DROP` chỉ khuyến nghị kiểm tra thiết bị.
- `LOW_BATTERY` chỉ khuyến nghị cắm sạc.
- `NETWORK_LOST` chỉ khuyến nghị kiểm tra kết nối.

### 3. Dữ liệu thiếu thì không forecast mạnh

Nếu thiếu timestamp, thiếu `battery_level` hoặc chưa đủ số mẫu, forecast trả fallback response với confidence thấp. Dashboard nên hiểu đây là tín hiệu chưa đủ chắc chắn.

### 4. Confidence thấp thì yêu cầu người dùng xác nhận

Khi `confidence` thấp, recommendation nên được hiểu là gợi ý cần xác nhận thủ công. Không dùng confidence thấp để ra quyết định tự động.

### 5. Safety note trong output

Anomaly output luôn có:

```text
AI chỉ cảnh báo, không tự động điều khiển thiết bị.
```

Forecast output luôn có:

```text
Forecast chỉ là tín hiệu khuyến nghị, không phải lệnh điều khiển.
```

Risk output luôn có:

```text
PhoneGuard AIoT chỉ khuyến nghị, không tự điều khiển thiết bị.
```

## Nguyên tắc trình bày trước giảng viên

- Nói rõ đây là baseline AIoT pipeline, chưa phải hệ thống safety-critical.
- Nhấn mạnh người dùng giữ quyền quyết định.
- Chỉ dùng forecast/risk như tín hiệu hỗ trợ.
- Giải thích được từng rule và từng file log.
