# ✅ Đã Quay Lại Sử Dụng Ollama (Miễn Phí)

## 📋 Tóm Tắt

Hệ thống chatbot đã được **restore lại** để sử dụng **Ollama** (local AI) thay vì DeepSeek API.

## ✅ File Đã Thay Đổi

### 1. `chatbot/client.py` ✅
- Đã restore lại code Ollama
- Loại bỏ DeepSeek API configuration
- Endpoint: `http://localhost:11434`
- Model: `gemma2:2b`

### 2. `main.py` ✅
- Cập nhật lại error messages để reference Ollama
- Loại bỏ các error handling cho DeepSeek (401, 429, API key)

### 3. Tài Liệu Mới 📚
- `docs/CAI_DAT_OLLAMA.md` - Hướng dẫn chi tiết cài đặt Ollama

## 🚀 Các Bước Tiếp Theo

### Bước 1: Cài Đặt Ollama

**Windows:**
1. Download tại: https://ollama.com/download
2. Chạy file cài đặt (OllamaSetup.exe)
3. Ollama sẽ tự động chạy

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Bước 2: Tải Model

Mở terminal/command prompt và chạy:
```bash
ollama pull gemma2:2b
```

### Bước 3: Chạy Ollama Server

**Windows:** Ollama tự động chạy sau khi cài (check system tray)

**Hoặc chạy thủ công:**
```bash
ollama serve
```

### Bước 4: Kiểm Tra

Mở browser và truy cập:
```
http://localhost:11434
```

Bạn sẽ thấy: **"Ollama is running"**

### Bước 5: Test Chatbot

1. Mở app Smart Scheduler (http://localhost:3000)
2. Vào trang Chatbot
3. Gửi tin nhắn: "xin chào"
4. Bot sẽ trả lời! 🎉

## 📊 Ưu Điểm của Ollama

✅ **Miễn phí 100%** - Không tốn tiền  
✅ **Chạy local** - Không cần internet  
✅ **Riêng tư** - Dữ liệu không gửi ra ngoài  
✅ **Không giới hạn** - Không có rate limit  
✅ **Offline** - Hoạt động khi mất mạng  

## ⚠️ Yêu Cầu Hệ Thống

- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
- **Disk**: ~2GB để lưu model gemma2:2b
- **CPU**: Bất kỳ (không cần GPU)

## 🔧 Troubleshooting

### Lỗi: "Không thể kết nối với Ollama"

**Kiểm tra:**
```bash
# Check Ollama có chạy không
curl http://localhost:11434

# Nếu không chạy, khởi động:
ollama serve
```

### Lỗi: "Model chưa được tải"

**Giải pháp:**
```bash
ollama pull gemma2:2b
ollama list  # Kiểm tra model đã có
```

## 📁 File Tham Khảo

- **Hướng dẫn chi tiết**: `docs/CAI_DAT_OLLAMA.md`
- **Code chatbot**: `smart-scheduler-api/chatbot/client.py`
- **Main API**: `smart-scheduler-api/main.py`

## 🔄 So Sánh: DeepSeek vs Ollama

| Feature | DeepSeek | Ollama |
|---------|----------|--------|
| Chi phí | Có phí 💰 | Miễn phí ✅ |
| Internet | Cần ☁️ | Không cần 🏠 |
| Tốc độ | Nhanh | Vừa phải |
| Giới hạn | Rate limit | Không giới hạn |
| Privacy | Cloud | Local ✅ |

## ⚡ Quick Commands

```bash
# Cài Ollama (Windows: download từ website)
curl -fsSL https://ollama.com/install.sh | sh  # macOS/Linux

# Pull model
ollama pull gemma2:2b

# Chạy server
ollama serve

# Test
ollama run gemma2:2b "xin chào"

# Xem models đã có
ollama list
```

---

**Status:** ✅ Code đã được restore về Ollama  
**Next Steps:** Cài đặt Ollama theo hướng dẫn ở trên  
**Docs:** Xem `docs/CAI_DAT_OLLAMA.md` để biết thêm chi tiết
