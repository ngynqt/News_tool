# Cafef Article Scraper & AI Facebook Summarizer

Một công cụ cào dữ liệu chi tiết bài viết từ Cafef bằng Python, sử dụng thư viện `requests`, `beautifulsoup4` và tích hợp **Gemini API** để phân tích và tự động soạn thảo bài viết đăng Facebook chuyên nghiệp. 

Công cụ đã được phát triển thêm **Giao diện Web (UI/UX) Glassmorphism sang trọng** và cơ chế cấu hình thông qua file `config.json`.

---

## Các tính năng nổi bật
- **Giao diện Web hiện đại:** Giao diện tối (Dark Mode) cao cấp kết hợp hiệu ứng kính (Glassmorphism), thiết kế responsive mượt mà trên cả máy tính và điện thoại.
- **Quản lý cấu hình API Key dễ dàng:** Quản lý khóa Gemini API thông qua tệp cấu hình `config.json` hoặc nhập trực tiếp ngay trên giao diện Web UI.
- **Trích xuất thông tin chi tiết:**
  - Tiêu đề (Title), Mô tả ngắn (Sapo), Ngày đăng bài (Publish Time).
  - Nội dung bài viết (Text Content) đã lọc bỏ chú thích ảnh để tránh trùng lặp dữ liệu.
  - Hình ảnh & Chú thích (Images & Captions) lấy liên kết ảnh gốc chất lượng cao.
- **Tóm tắt bài đăng Facebook bằng AI:** Sử dụng mô hình `gemini-1.5-flash` để tự động soạn thảo bài viết đăng Facebook chuyên nghiệp (bao gồm tiêu đề, biểu tượng emoji, tóm tắt ý chính dạng danh sách, hashtag phù hợp và link bài viết gốc). Có sẵn nút bấm **Sao chép một chạm** để đăng ngay lên Facebook.
- **Chế độ dòng lệnh (CLI):** Vẫn giữ nguyên khả năng chạy nhanh qua Terminal để xuất dữ liệu ra tệp JSON.

---

## Cấu trúc thư mục dự án
```text
News_tool/
├── app.py             # Máy chủ Flask & Giao diện Web UI (HTML/CSS/JS)
├── cafef_scraper.py   # Module cào dữ liệu cốt lõi & CLI tool
├── config.json        # Tệp lưu cấu hình Gemini API Key
└── README.md          # Hướng dẫn sử dụng này
```

---

## Hướng dẫn cài đặt

### 1. Cài đặt các thư viện cần thiết:
Chạy lệnh sau trên Terminal để cài đặt các thư viện hỗ trợ bằng tệp `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## Hướng dẫn sử dụng

### Cách 1: Sử dụng Giao diện Web UI (Dễ sử dụng nhất)

1. **Khởi động server Flask:**
   ```bash
   python3 app.py
   ```
2. **Truy cập vào giao diện:**
   Mở trình duyệt web của bạn và truy cập địa chỉ: [http://localhost:5000](http://localhost:5000)
3. **Cấu hình & Sử dụng:**
   - Mở rộng phần **Cấu hình API Gemini Key** và nhập khóa API của bạn vào rồi nhấn **Lưu khóa**. (Khóa sẽ được lưu trực tiếp vào tệp `config.json` ở máy bạn).
   - Dán URL bài viết Cafef vào ô nhập liệu và nhấn **Cào & Phân tích**.
   - Xem bài viết chi tiết bên cột trái, và bản dự thảo đăng Facebook kèm ảnh bên cột phải. Click **Sao chép** để copy bài đăng.

---

### Cách 2: Sử dụng dòng lệnh (CLI)

#### Xuất dữ liệu cơ bản (Không sử dụng AI)
Lưu trực tiếp dữ liệu bài viết vào tệp `output.json` và hiển thị trên màn hình:
```bash
python3 cafef_scraper.py "https://cafef.vn/ba-dieu-anh-chi-gan-tram-ty-dong-om-15-co-phan-mot-doanh-nghiep-xay-dung-188260706234810936.chn"
```

#### Sử dụng Gemini để tóm tắt bài đăng Facebook qua CLI
Cách hoạt động sẽ ưu tiên lấy API Key từ `config.json` (nếu đã cấu hình trên Web) hoặc bạn có thể chỉ định qua dòng lệnh:

**Cách A (Truyền khóa qua biến môi trường):**
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
python3 cafef_scraper.py "https://cafef.vn/ba-dieu-anh-chi-gan-tram-ty-dong-om-15-co-phan-mot-doanh-nghiep-xay-dung-188260706234810936.chn"
```

**Cách B (Truyền khóa trực tiếp qua tham số `-k`):**
```bash
python3 cafef_scraper.py "https://cafef.vn/ba-dieu-anh-chi-gan-tram-ty-dong-om-15-co-phan-mot-doanh-nghiep-xay-dung-188260706234810936.chn" -k "your-gemini-api-key-here"
```

**Cách chọn Model qua dòng lệnh (Sử dụng tham số `-m` hoặc `--model`):**
```bash
# Sử dụng model gemini-1.5-pro thay vì flash
python3 cafef_scraper.py "https://cafef.vn/..." -k "your-gemini-api-key-here" -m "gemini-1.5-pro"
```

*Nếu bạn không truyền tham số `-m`, script sẽ tự động tìm trường `"gemini_model"` trong `config.json` hoặc mặc định dùng `gemini-1.5-flash`.*

---

## Cấu trúc dữ liệu lưu trong JSON
Dữ liệu lưu trữ trong tệp `output.json` có cấu trúc rõ ràng như sau:
```json
{
  "url": "https://cafef.vn/...",
  "title": "Bà Diệu Anh chi gần trăm tỷ đồng...",
  "sapo": "Cá nhân này đã thực hiện...",
  "publish_time": "07-07-2026 - 00:03 AM",
  "content": "Trong thông báo mới nhất...",
  "images": [
    {
      "url": "https://cafefcdn.com/...",
      "caption": "Đối tượng A và B"
    }
  ],
  "facebook_summary": "📝 DỰ THẢO BÀI ĐĂNG FACEBOOK...\n\n🚀 TIÊU ĐỀ..."
}
```
