# Hướng Dẫn Chuyển Đổi Chatbot từ Ollama sang DeepSeek API

## Tổng Quan

Tài liệu này mô tả quá trình chuyển đổi hệ thống chatbot của Smart Scheduler từ việc sử dụng Ollama (local AI model) sang DeepSeek API (cloud-based AI service).

## Lý Do Chuyển Đổi

- **Không cần cài đặt local**: Không cần cài đặt và chạy Ollama server
- **Hiệu suất ổn định**: Sử dụng cloud API có băng thông và hiệu suất tốt hơn
- **Dễ triển khai**: Không cần GPU hoặc tài nguyên máy mạnh để chạy AI model
- **Chi phí hợp lý**: DeepSeek cung cấp API với giá cạnh tranh

## Các Thay Đổi Đã Thực Hiện

### 1. File `chatbot/client.py`

**Trước đây (Ollama):**
```python
OLLAMA_API_URL = "http://localhost:11434/api/chat"

payload = {
    "model": "gemma2:2b",
    "messages": messages,
    "stream": False
}

async with session.post(OLLAMA_API_URL, json=payload, ...) as resp:
    # Xử lý response
```

**Hiện tại (DeepSeek):**
```python
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-b9af060eba7b4c2bbac1e6eae87b7381"

payload = {
    "model": "deepseek-chat",
    "messages": messages,
    "temperature": 0.8,
    "max_tokens": 2048,
    "stream": False
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
}

async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers, ...) as resp:
    # Xử lý response theo OpenAI format
```

**Điểm khác biệt chính:**
- Sử dụng HTTPS endpoint thay vì localhost
- Cần API key cho authentication
- Response format tương thích với OpenAI API (sử dụng `choices[0].message.content`)
- Thêm các tham số như `temperature` và `max_tokens` để kiểm soát chất lượng response

### 2. File `main.py`

**Cập nhật thông báo lỗi:**

Trước đây:
```python
if "connection" in error_str:
    error_message = "Xin lỗi, tôi không thể kết nối với mô hình AI. Vui lòng kiểm tra Ollama đã được khởi động chưa..."
elif "model" in error_str:
    error_message = "Xin lỗi, mô hình AI chưa được tải. Vui lòng chạy 'ollama pull gemma2:2b'..."
```

Hiện tại:
```python
if "connection" in error_str:
    error_message = "Xin lỗi, tôi không thể kết nối với DeepSeek API. Vui lòng kiểm tra kết nối internet..."
elif "api key" in error_str or "401" in error_str:
    error_message = "Xin lỗi, API key không hợp lệ. Vui lòng kiểm tra cấu hình DeepSeek API."
elif "429" in error_str:
    error_message = "Xin lỗi, đã vượt quá giới hạn sử dụng API. Vui lòng thử lại sau."
```

## Cách Sử Dụng

### 1. Cấu Hình API Key

API key đã được cấu hình trực tiếp trong file `chatbot/client.py`:
```python
DEEPSEEK_API_KEY = "sk-b9af060eba7b4c2bbac1e6eae87b7381"
```

**Lưu ý bảo mật:** Trong môi trường production, nên lưu API key trong biến môi trường:
```python
import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-b9af060eba7b4c2bbac1e6eae87b7381")
```

### 2. Khởi Động Hệ Thống

Không cần cài đặt hay khởi động Ollama nữa. Chỉ cần chạy server như bình thường:

```bash
cd smart-scheduler-api
uvicorn main:app --reload
```

### 3. Test Chatbot

Truy cập vào trang web và sử dụng tính năng chatbot. Chatbot sẽ tự động kết nối với DeepSeek API.

## Xử Lý Lỗi

Hệ thống đã được cập nhật để xử lý các lỗi phổ biến:

1. **Lỗi kết nối (Connection Error)**: Kiểm tra kết nối internet
2. **Lỗi 401 (Unauthorized)**: API key không hợp lệ
3. **Lỗi 429 (Rate Limit)**: Đã vượt quá giới hạn sử dụng API
4. **Lỗi 500 (Server Error)**: Server DeepSeek đang gặp sự cố
5. **Timeout**: Yêu cầu hết thời gian chờ (60 giây)

## Ưu Điểm của DeepSeek API

1. **Không cần cài đặt**: Không cần cài đặt Ollama, model, hay dependencies khác
2. **Hiệu suất cao**: Response nhanh và ổn định
3. **Hỗ trợ tiếng Việt tốt**: DeepSeek model hiểu và trả lời tiếng Việt tự nhiên
4. **Dễ scale**: Có thể xử lý nhiều request đồng thời
5. **Không cần GPU**: Không cần phần cứng mạnh

## Nhược Điểm và Lưu Ý

1. **Cần internet**: Phải có kết nối internet để sử dụng
2. **Chi phí API**: Có thể phát sinh chi phí khi sử dụng (xem [DeepSeek Pricing](https://platform.deepseek.com/pricing))
3. **Rate limits**: Có giới hạn số request mỗi phút/ngày tùy theo gói
4. **Bảo mật**: Dữ liệu chat được gửi đến server bên thứ ba

## API Documentation

Tham khảo thêm tại: https://platform.deepseek.com/api-docs/

## Rollback về Ollama (Nếu Cần)

Nếu muốn quay lại sử dụng Ollama, có thể uncomment code cũ trong `chatbot/client.py` và comment code DeepSeek hiện tại.

## Kết Luận

Việc chuyển đổi sang DeepSeek API giúp hệ thống dễ triển khai và sử dụng hơn, đặc biệt phù hợp với môi trường production không có sẵn GPU hay tài nguyên để chạy local AI models.
