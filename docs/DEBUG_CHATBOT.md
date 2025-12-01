# Debug Chatbot Connection Issue

## Vấn Đề
Chatbot báo lỗi "Không thể kết nối đến server" khi sử dụng trong UI.

## Đã Làm
✅ Test DeepSeek API trực tiếp - **THÀNH CÔNG**  
✅ Server đang chạy tốt - **OK**  
✅ Thêm debug logging vào `chatbot/client.py`

## Bước Tiếp Theo - Vui Lòng Làm Theo

### 1. Refresh lại trang web
- Mở browser
- Nhấn **Ctrl + Shift + R** (hard refresh) để xóa cache
- Hoặc **Ctrl + F5**

### 2. Thử chat lại
- Gửi tin nhắn: "xin chào"
- **QUAN TRỌNG**: Xem terminal đang chạy `uvicorn` 

### 3. Copy log từ terminal
Sau khi gửi tin nhắn, bạn sẽ thấy log như thế này:
```
[DEBUG] Calling DeepSeek API with message: xin chào...
[DEBUG] API URL: https://api.deepseek.com/v1/chat/completions
[DEBUG] Using API Key: sk-b9af060...
```

**Hãy copy toàn bộ log và gửi cho tôi!**

### 4. Kiểm tra Browser Console
- Nhấn **F12** để mở DevTools
- Chuyển sang tab **Console**
- Xem có lỗi gì màu đỏ không?
- Copy lỗi đó cho tôi

## Nguyên Nhân Có Thể

1. **Server chưa reload**: Uvicorn có thể chưa nhận thay đổi
2. **Browser cache**: Frontend còn dùng code cũ
3. **CORS issue**: Có thể bị chặn bởi CORS policy
4. **Token invalid**: JWT token hết hạn

## Cách Khắc Phục Nhanh

### Option 1: Restart Server
Trong terminal đang chạy uvicorn:
1. Nhấn **Ctrl + C** để dừng
2. Chạy lại: `uvicorn main:app --reload`

### Option 2: Clear Browser
1. Logout khỏi app
2. Clear cache/cookies  
3. Login lại
4. Thử chat

## File Debug Scripts

- `test_deepseek.py` - Test DeepSeek API trực tiếp ✅ PASSED
- `test_server.py` - Test server đang chạy ✅ OK  
- Giờ cần test qua UI để xem log

---

**ACTION REQUIRED**: Vui lòng làm theo bước 1-4 ở trên và gửi log cho tôi!
