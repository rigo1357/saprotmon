# Hướng dẫn khắc phục lỗi Ollama

## Lỗi: "bind: Only one usage of each socket address"

### Nguyên nhân
Lỗi này xảy ra khi bạn cố gắng chạy `ollama serve` nhưng Ollama đã đang chạy rồi. Port 11434 đã được sử dụng.

### Giải pháp

#### 1. Kiểm tra Ollama đã chạy chưa
```bash
# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

# Hoặc kiểm tra port
netstat -ano | findstr :11434
```

#### 2. Nếu Ollama đã chạy
**Không cần làm gì!** Ollama đã sẵn sàng sử dụng. Bạn có thể:
- Test kết nối: Mở browser và truy cập http://localhost:11434
- Kiểm tra models: `ollama list`

#### 3. Nếu muốn restart Ollama
```bash
# Tìm process ID
netstat -ano | findstr :11434

# Kill process (thay PID bằng số bạn tìm được)
taskkill /PID <PID> /F

# Sau đó chạy lại
ollama serve
```

#### 4. Kiểm tra model đã được tải chưa
```bash
ollama list
```

Nếu không có `gemma2:9b` hoặc `gemma2:2b`, chạy:
```bash
ollama pull gemma2:9b
# hoặc
ollama pull gemma2:2b
```

## Test chatbot

Sau khi đảm bảo Ollama đang chạy và model đã được tải:
1. Khởi động API: `cd smart-scheduler-api && python main.py`
2. Khởi động Frontend: `cd smart-scheduler-ui && npm start`
3. Đăng nhập và test chatbot

Nếu vẫn gặp lỗi, kiểm tra:
- Ollama đang chạy trên port 11434
- Model đã được tải (`ollama list`)
- Firewall không chặn port 11434

