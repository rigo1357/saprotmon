# 🤖 Hướng dẫn sử dụng Chatbot Tsundere AI

## 📋 Tổng quan

Chatbot trong Smart Scheduler sử dụng Ollama với model Gemma2 để tạo ra một trợ lý AI có tính cách tsundere (kiểu nhân vật anime lạnh lùng bên ngoài nhưng ấm áp bên trong).

## 🚀 Cài đặt và Cấu hình

### 1. Cài đặt Ollama

**Windows:**
- Tải Ollama từ: https://ollama.ai/download
- Cài đặt và chạy ứng dụng

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Khởi động Ollama Server

Mở terminal và chạy:
```bash
ollama serve
```

Server sẽ chạy trên `http://localhost:11434`

### 3. Tải Model AI

Có 2 lựa chọn model:

**Option 1: Gemma2:9b (Khuyến nghị - Chất lượng tốt hơn)**
```bash
ollama pull gemma2:9b
```

**Option 2: Gemma2:2b (Nhẹ hơn, nhanh hơn)**
```bash
ollama pull gemma2:2b
```

Chatbot sẽ tự động fallback về model 2b nếu không tìm thấy model 9b.

## 💬 Cách sử dụng

### Trong ứng dụng:

1. Đăng nhập vào Smart Scheduler
2. Chuyển sang tab **"💬 Trợ lý AI"**
3. Bắt đầu chat với chatbot

### Tính năng:

- **Hỗ trợ xếp lịch học**: Hỏi về cách sử dụng hệ thống
- **Tư vấn môn học**: Tư vấn về các môn học, chuyên ngành
- **Giải đáp thắc mắc**: Trả lời các câu hỏi về Smart Scheduler
- **Tính cách tsundere**: Chatbot có tính cách đặc biệt, hay trêu chọc nhưng rất quan tâm

### Ví dụ câu hỏi:

- "Làm sao để xếp lịch học?"
- "Em có thể giúp anh chọn môn học không?"
- "Học kỳ này nên học những môn gì?"
- "Chuyên ngành CNTT có những môn gì?"

## 🔧 Xử lý lỗi

### Lỗi: "Không thể kết nối với Ollama"

**Nguyên nhân:** Ollama server chưa chạy

**Giải pháp:**
```bash
ollama serve
```

### Lỗi: "Model không tìm thấy"

**Nguyên nhân:** Chưa tải model

**Giải pháp:**
```bash
ollama pull gemma2:9b
# hoặc
ollama pull gemma2:2b
```

### Lỗi: "Timeout"

**Nguyên nhân:** Model quá lớn hoặc máy tính yếu

**Giải pháp:**
- Sử dụng model nhẹ hơn: `gemma2:2b`
- Tăng timeout trong code (mặc định 60s cho 9b, 30s cho 2b)

## 📝 Cấu hình nâng cao

### Thay đổi Model

Sửa file `smart-scheduler-api/chatbot/client.py`:

```python
model_name = "gemma2:9b"  # Đổi thành model bạn muốn
```

### Thay đổi Temperature

Temperature cao hơn = phản hồi tự nhiên hơn nhưng có thể ít chính xác hơn:

```python
temperature=0.8  # Mặc định 0.8, có thể điều chỉnh 0.1-1.0
```

### Thay đổi Prompt

Sửa biến `PROMPT` trong `smart-scheduler-api/chatbot/client.py` để thay đổi tính cách và hành vi của chatbot.

## 🎯 Tính năng đặc biệt

- **Auto-fallback**: Tự động chuyển sang model 2b nếu không tìm thấy 9b
- **Error handling**: Xử lý lỗi thân thiện với thông báo dễ hiểu
- **Tsundere personality**: Tính cách đặc biệt, phù hợp với người dùng yêu thích anime

## 📚 Tài liệu tham khảo

- Ollama: https://ollama.ai
- Gemma2 Model: https://huggingface.co/google/gemma-2

