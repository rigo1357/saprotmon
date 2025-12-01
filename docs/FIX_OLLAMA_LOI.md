# ⚠️ LỖI: Ollama Chưa Chạy

## 🔴 Vấn Đề Hiện Tại

Chatbot báo lỗi vì **Ollama chưa được cài đặt hoặc chưa chạy**.

**Lỗi từ server:**
```
ConnectionRefusedError: Cannot connect to host localhost:11434
Exception: Không thể kết nối đến Ollama
```

## ✅ GIẢI PHÁP NHANH

### Bước 1: Cài Đặt Ollama (Windows)

1. **Download Ollama**
   ```
   https://ollama.com/download/windows
   ```
   Hoặc trực tiếp: https://ollama.com/download/OllamaSetup.exe

2. **Chạy file cài đặt**
   - Double click file `OllamaSetup.exe`
   - Follow wizard cài đặt
   - Ollama sẽ tự động chạy sau khi cài xong

### Bước 2: Tải Model

Mở **PowerShell** hoặc **Command Prompt** (Terminal mới, không phải uvicorn):

```powershell
ollama pull gemma2:2b
```

**Đợi khoảng 2-5 phút** để tải ~1.6GB

### Bước 3: Kiểm Tra Ollama Đang Chạy

Cách 1 - Check trong terminal:
```powershell
curl http://localhost:11434
```

Cách 2 - Mở browser:
```
http://localhost:11434
```

**Kết quả mong đợi:** "Ollama is running" ✅

### Bước 4: Test Ngay

```powershell
ollama run gemma2:2b "xin chào"
```

Nếu model trả lời → **Thành công!**

### Bước 5: Thử Lại Chatbot

1. Quay lại app (http://localhost:3000)
2. Refresh trang (Ctrl+F5)
3. Gửi tin nhắn trong chatbot
4. **Bot sẽ trả lời!** 🎉

## 🚨 Nếu Ollama Không Tự Động Chạy

Sau khi cài xong, nếu vẫn lỗi:

**Chạy thủ công:**
```powershell
ollama serve
```

**Kiểm tra lại:**
```powershell
curl http://localhost:11434
```

## 📋 Commands Tóm Tắt

```powershell
# 1. Cài Ollama (download từ website)

# 2. Pull model
ollama pull gemma2:2b

# 3. Check Ollama chạy chưa
curl http://localhost:11434

# 4. Nếu chưa chạy:
ollama serve

# 5. Test
ollama run gemma2:2b "xin chào"
```

## 💡 Lưu Ý

- Ollama cần **~2GB disk** cho model
- Cần **4GB RAM** tối thiểu
- **Không cần GPU**
- Windows 10/11 đều được

## 🔗 Links Hữu Ích

- **Download:** https://ollama.com/download
- **Docs:** https://github.com/ollama/ollama/blob/main/docs/windows.md
- **Models:** https://ollama.com/library

---

**TÓM TẮT:**
1. Download Ollama từ https://ollama.com/download/windows
2. Cài đặt
3. Chạy: `ollama pull gemma2:2b`
4. Thử lại chatbot!
