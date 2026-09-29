# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: viết nhận xét dựa trên các lần chạy thực tế của bài lab.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Nguyễn Tất Đạt  Mã học viên: 2A202602578

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu quên đặt `AGENT_API_KEY` khi tạo service Railway, tiến trình sẽ báo lỗi cấu hình ngay lúc startup và bản deploy không qua healthcheck. Tôi sẽ thấy lỗi trong deploy log trước khi phát hành URL mới. Nếu code dùng khóa mặc định `changeme`, service vẫn Online và người biết khóa mặc định có thể gọi `/ask`, tạo request và chi phí trên tài khoản của tôi.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Một dòng tôi lấy từ Railway deployment log ở chế độ JSON sau khi gọi `/ask`:

```json
{"tokens_out":45,"tokens_in":41,"event":"ask_completed","timestamp":"2026-09-29T04:40:43.171949+00:00","user_id":"cp5-test","level":"info","cost_usd":0.00003315,"message":""}
```

Tôi có thể lọc `event=ask_completed` và `user_id=cp5-test` để truy vết riêng request của một user; đồng thời cộng `cost_usd` hoặc đếm `tokens_in` theo thời gian để theo dõi chi phí. Dòng `print("đã trả lời xong")` không có các trường máy đọc được để thực hiện hai việc đó.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1,73 GB (`day12-agent:single`, build từ Dockerfile ở commit starter) |
| Multi-stage | 297 MB (`day12-agent:prod`, đo bằng `docker images`) |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Tôi build cả hai trên cùng máy và đo bằng `docker images`: 1,73 GB so với 297 MB, giảm khoảng 1,43 GB. Starter dùng `python:3.11` bản đầy đủ, cài dependency ngay trong image cuối và `COPY . .`; image mới dùng `python:3.11-slim`, chỉ chép package đã cài từ builder sang runtime. Phần lớn chênh lệch đến từ việc đổi base image đầy đủ sang slim; multi-stage còn giữ file và trạng thái build của builder ra khỏi runtime. Vì hai yếu tố thay đổi cùng lúc, không thể quy toàn bộ 1,43 GB cho riêng multi-stage.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Tôi build trên bản sao tạm, thêm một dòng comment vào `app/main.py` rồi build lại. BuildKit báo `CACHED` cho `COPY requirements.txt`, `RUN pip install`, tạo user và `COPY --from=builder`; `COPY app/` và `COPY utils/` chạy lại vì chúng nằm sau layer source thay đổi. Nếu đặt `COPY . .` trước `RUN pip install`, mỗi lần sửa code sẽ đổi checksum của layer COPY và buộc pip chạy lại dù `requirements.txt` không đổi.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Nếu một lỗ hổng cho phép thực thi lệnh trong process Python, mã độc nhận quyền của user đang chạy process đó. Khi process là root trong container, kẻ tấn công có quyền rộng hơn với filesystem, volume và các khả năng container được cấp; kết hợp cấu hình host nguy hiểm hoặc lỗi container escape có thể dẫn đến quyền cao trên host. `USER agent` làm process chỉ có quyền của user thường, cắt bớt quyền ngay tại bước thực thi lệnh. Đây là giảm thiểu tác động, không phải bảo đảm tuyệt đối chống container escape.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Với bộ đếm reset ở giây 00, user có thể gửi 10 request ở cuối phút trước (ví dụ 12:00:59) rồi 10 request ngay đầu phút sau (12:01:00): tổng 20 request trong khoảng 2 giây dù giới hạn danh nghĩa là 10/phút. Sliding window 60 giây vẫn nhìn thấy 10 request đầu nên chặn nhóm thứ hai.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Rate limit khống chế tốc độ theo cửa sổ 60 giây; cost guard khống chế tổng tiền trong tháng UTC. Một request đầu tiên trong phút vẫn có thể bị cost guard trả 402 nếu `spent + estimated_cost` vượt 10 USD. Ngược lại, user còn nhiều ngân sách nhưng gửi request thứ 11 trong 60 giây sẽ bị limiter trả 429. Trên URL Railway, tôi đã thấy 10 request đầu trả 200 và 5 request tiếp theo trả 429.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Nếu Redis mất kết nối 30 giây và `/health` cũng kiểm tra Redis, cả 3 container sẽ đồng loạt báo không khỏe dù process Python vẫn chạy. Load balancer có thể ngừng gửi traffic; nếu orchestrator dùng endpoint đó làm liveness probe, nó còn restart cả 3 container, tạo vòng lặp startup trong lúc Redis vẫn lỗi. Khi tách probe, `/health` vẫn trả 200 vì process còn sống, còn `/ready` trả 503 để tạm ngừng nhận request. Redis phục hồi thì `/ready` trả 200 và traffic quay lại mà không cần restart process.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Tôi đã scale Compose lên 3 agent và gọi `/ask` cùng user qua các instance: `history_length` quan sát được tăng 0 → 2 → 4, kể cả sau khi một instance restart. Mỗi lượt hỏi thêm message user và assistant vào Redis List chung. Nếu dùng dict Python, mỗi container có lịch sử riêng: request chuyển sang container khác có thể thấy độ dài quay về 0 hoặc một giá trị cũ; restart instance cũng xóa lịch sử của nó.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Lỗi thực tế trong quá trình deploy Railway là CLI trả `Unauthorized. Please login with railway login` khi tôi chạy `railway whoami`. Tôi kiểm tra lại trạng thái đăng nhập và thấy trình duyệt đã đăng nhập Railway nhưng CLI chưa có phiên OAuth riêng. Tôi chạy `railway login --browserless`, ủy quyền cho đúng project lab, rồi `railway whoami` báo đăng nhập thành công. Sau đó `railway up` deploy thành công, build log báo healthcheck `/health` thành công và URL thật trả `/ready` với `redis: true`.
