# Thông tin triển khai — Checkpoint 5

## Thông tin học viên

| Mục | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Tất Đạt |
| Mã học viên | 2A202602578 |
| Repository cá nhân | https://github.com/Gaohonggg/K4-L3B-DAY12-NguyenTatDat-2A202602578-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
| --- | --- |
| Public URL | https://day12-agent-production-9fb1.up.railway.app |
| Platform | Railway |
| Ngày triển khai | 2026-09-29 |
| Railway service | `day12-agent` |
| Redis | Railway Redis service, kết nối qua private network |
| Nguồn triển khai | `railway up` từ thư mục làm bài; Dockerfile multi-stage |

## Biến môi trường trên Railway

Chỉ ghi tên biến và nguồn cấu hình; không lưu giá trị secret vào repository.

| Biến | Nguồn |
| --- | --- |
| `PORT` | Railway tự cấp; ứng dụng đọc tại thời điểm chạy |
| `AGENT_API_KEY` | Secret của service `day12-agent`, nạp từ `.env` cục bộ qua stdin của Railway CLI |
| `REDIS_URL` | Tham chiếu `${{Redis.REDIS_URL}}` đến Redis service trong cùng project |
| `RATE_LIMIT_PER_MINUTE` | Railway Variables: `10` |
| `MONTHLY_BUDGET_USD` | Railway Variables: `10.0` |
| `LOG_LEVEL` | Railway Variables: `INFO` |

## Kiểm tra trên public URL

Các lệnh sau đã chạy ngày 2026-09-29. Khi tự kiểm tra request có xác thực, đặt `DEPLOY_API_KEY` ở môi trường cục bộ; không đưa key vào lệnh đã lưu, log hoặc tài liệu.

```bash
URL=https://day12-agent-production-9fb1.up.railway.app

curl -i "$URL/health"
curl -i "$URL/ready"
curl -i -X POST "$URL/ask" \
  -H 'Content-Type: application/json' \
  -d '{"question":"Hello"}'

curl -i -X POST "$URL/ask" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $DEPLOY_API_KEY" \
  -H 'X-User-Id: cp5-verified' \
  -d '{"question":"Deploy là gì?"}'
```

Kết quả thực tế (đã lược bỏ response headers và không hiển thị key):

```text
GET  /health           200 {"status":"ok","service":"day12-agent","version":"1.0.0"}
GET  /ready            200 {"status":"ready","redis":true}
POST /ask thiếu key    401 {"detail":"invalid or missing API key"}
POST /ask có key       200; response có answer, cost_usd, history_length, tokens, user_id

15 POST /ask liên tiếp với cùng X-User-Id:
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

Railway build log xác nhận image được build từ Dockerfile và healthcheck `/health` thành công. Runtime log xác nhận Uvicorn bind `0.0.0.0:8080`, là cổng do Railway cấp.

## Ảnh chụp màn hình

- `screenshots/dashboard.png`: dashboard Railway hiển thị service agent và Redis.
- `screenshots/health.png`: kết quả gọi `/health` trên public URL.
