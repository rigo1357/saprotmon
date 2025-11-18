# 📚 Scripts - Hướng dẫn sử dụng

## 🎓 Thêm môn học mẫu

Script `add_sample_courses.py` giúp thêm các môn học mẫu cho các ngành khác nhau vào database.

### Cách sử dụng:

1. **Đảm bảo đã có admin user:**
   - Đăng nhập với tài khoản admin
   - Hoặc tài khoản admin sẽ được tạo tự động khi server khởi động

2. **Chạy script:**
   ```bash
   cd smart-scheduler-api
   python scripts/add_sample_courses.py
   ```

3. **Kết quả:**
   - Script sẽ thêm các môn học mẫu cho các ngành:
     - **CNTT** (Công nghệ Thông tin)
     - **KT** (Kinh tế)
     - **NN** (Ngoại ngữ)
     - **TOAN** (Toán)
     - **VATLY** (Vật lý)
     - **HOA** (Hóa học)
   - Các học kỳ: 2024-1, 2024-2

### Dữ liệu mẫu:

- **Học kỳ 2024-1:**
  - CNTT: 8 môn (INT1001-INT4002)
  - KT: 8 môn (Kế toán, Tài chính, Quản trị)
  - NN: 6 môn (Tiếng Anh, Nhật, Trung, Hàn)
  - TOAN: 6 môn (Giải tích, Đại số, Xác suất...)
  - VATLY: 4 môn (Vật lý đại cương, Cơ học lượng tử...)
  - HOA: 3 môn (Hóa học đại cương, Hữu cơ, Vô cơ)

- **Học kỳ 2024-2:**
  - CNTT: 4 môn bổ sung
  - KT: 2 môn bổ sung

### Lưu ý:

- Script sẽ **bỏ qua** các môn học đã tồn tại (dựa trên code + semester + major)
- Mỗi môn học sẽ được gán cho admin user hiện tại
- Có thể chạy lại script nhiều lần mà không lo trùng lặp

### Tùy chỉnh:

Để thêm môn học mới, chỉnh sửa dictionary `SAMPLE_COURSES` trong file `add_sample_courses.py`:

```python
SAMPLE_COURSES = {
    "2024-1": {
        "CNTT": [
            {"code": "INT1001", "name": "Tên môn học", "credits": 3, "department": "Khoa CNTT"},
            # Thêm môn học mới ở đây
        ],
    }
}
```

