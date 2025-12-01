# Hướng Dẫn Cài Đặt và Sử Dụng Ollama

## 📥 Cài Đặt Ollama

### Windows

1. **Download Ollama**
   - Truy cập: https://ollama.com/download
   - Tải bản **Windows** (OllamaSetup.exe)
   - Chạy file cài đặt

2. **Cài đặt xong, Ollama sẽ tự động chạy**
   - Kiểm tra: Tìm biểu tượng Ollama ở system tray (góc dưới bên phải)

### macOS

```bash
# Download và cài đặt
curl -fsSL https://ollama.com/install.sh | sh
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 🚀 Tải Model Gemma2

Sau khi cài Ollama, mở terminal/command prompt và chạy:

```bash
# Pull model gemma2:2b (nhẹ, ~1.6GB)
ollama pull gemma2:2b
```

**Hoặc** model lớn hơn (nếu máy mạnh):
```bash
# gemma2:9b (tốt hơn nhưng nặng hơn, ~5.4GB)
ollama pull gemma2:9b
```

## ▶️ Khởi Động Ollama Server

### Windows
Ollama thường tự động chạy sau khi cài đặt. Nếu không:

1. Tìm **Ollama** trong Start Menu
2. Chạy ứng dụng
3. Hoặc mở terminal và chạy: `ollama serve`

### macOS/Linux
```bash
ollama serve
```

Nếu bạn thấy message: "Error: listen tcp 127.0.0.1:11434: bind: address already in use"
→ **Tốt!** Nghĩa là Ollama đã chạy rồi.

## ✅ Kiểm Tra Ollama Đang Chạy

Mở browser và truy cập:
```
http://localhost:11434
```

Bạn sẽ thấy message: **"Ollama is running"**

## 🧪 Test Ollama

Chạy terminal mới và test:

```bash
ollama run gemma2:2b "xin chào"
```

Nếu model trả lời → **Thành công!** ✅

## 🔧 Cấu Hình cho Smart Scheduler

Sau khi Ollama chạy, hệ thống Smart Scheduler sẽ tự động kết nối thông qua:
- **URL**: `http://localhost:11434`
- **Model**: `gemma2:2b`

Server FastAPI sẽ tự động reload với code mới (Ollama).

## 🎯 Sử Dụng Chatbot

1. **Đảm bảo Ollama đang chạy**
   - Check tại: http://localhost:11434

2. **Mở ứng dụng Smart Scheduler**
   - URL: http://localhost:3000
   
3. **Vào trang Chatbot**
   - Gửi tin nhắn test: "xin chào"
   
4. **Bot sẽ trả lời!** 🎉

## ⚠️ Troubleshooting

### Lỗi: "Không thể kết nối với Ollama"

**Giải pháp:**
```bash
# Khởi động Ollama
ollama serve
```

### Lỗi: "Model chưa được tải"

**Giải pháp:**
```bash
# Pull model
ollama pull gemma2:2b

# Kiểm tra model đã có chưa
ollama list
```

### Lỗi: Port 11434 đã được sử dụng

**Nguyên nhân:** Ollama đã chạy rồi!
- Không cần làm gì cả ✅

### Chatbot phản hồi chậm

**Nguyên nhân:** Model đang load lần đầu
- Lần đầu tiên sẽ chậm (5-10 giây)
- Các lần sau sẽ nhanh hơn

## 📊 So Sánh Models

| Model | Kích thước | RAM cần | Tốc độ | Chất lượng |
|-------|-----------|---------|--------|------------|
| gemma2:2b | 1.6 GB | 4 GB | Nhanh ⚡ | Tốt ✅ |
| gemma2:9b | 5.4 GB | 8 GB | Chậm hơn | Rất tốt ✨ |

**Khuyến nghị:** Dùng **gemma2:2b** cho phần lớn máy.

## 💡 Tips

1. **Để Ollama chạy liên tục**: Thêm Ollama vào startup của Windows
2. **Nhiều models**: Có thể pull nhiều model và switch giữa chúng
3. **Update model**: Chạy `ollama pull gemma2:2b` để update lên version mới

## 🔗 Tài Liệu Thêm

- Ollama Official: https://ollama.com
- Ollama GitHub: https://github.com/ollama/ollama
- Available Models: https://ollama.com/library

---

**Status sau khi cài đặt:**
✅ Ollama installed  
✅ Model gemma2:2b pulled  
✅ Ollama server running  
✅ Chatbot ready to use!
