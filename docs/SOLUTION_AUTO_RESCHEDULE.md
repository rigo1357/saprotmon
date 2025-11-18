# Giải pháp Tự động Xếp Lại Môn Học Bị Trùng

## Vấn đề hiện tại
Khi các môn học bị trùng lịch, hệ thống chỉ loại bỏ môn học đó thay vì tự động tìm sessions (nhóm/lớp) khác của cùng môn học để thay thế.

## Giải pháp đề xuất

### 1. Cấu trúc dữ liệu
Mỗi môn học có nhiều sessions (20-21 sessions) với:
- Cùng `original_code` (ví dụ: INT1003)
- Code duy nhất cho mỗi session (ví dụ: INT1003-G01, INT1003-G02, ...)
- Thời gian khác nhau (ngày, giờ, tuần)

### 2. Flow xử lý trùng lịch

```
Khi phát hiện trùng lịch:
1. Xác định môn học bị trùng (remove_entry)
2. Lấy original_code từ metadata
3. Query database: Tìm tất cả courses có metadata.original_code = original_code
4. Lọc các sessions:
   - Không trùng với môn học đang giữ lại (keep_entry)
   - Không trùng với các môn học khác trong active_entries
5. Nếu tìm thấy → Thay thế session
6. Nếu không tìm thấy → Loại bỏ môn học
```

### 3. Implementation

#### Backend (main.py)
```python
# Trong hàm handle_schedule, trước khi loại bỏ môn học:
def find_alternative_sessions_from_db(original_code, semester, conflicting_with, all_active_entries):
    """Tìm sessions thay thế từ database"""
    # Query database
    courses = await Course.find({
        "metadata.original_code": original_code,
        "semester": semester
    }).to_list()
    
    alternatives = []
    for course in courses:
        # Kiểm tra không trùng với môn đang conflict
        if not conflicts_with_entry(course, conflicting_with):
            # Kiểm tra không trùng với các môn khác
            has_conflict = False
            for active_entry in all_active_entries:
                if conflicts_with_course(course, active_entry):
                    has_conflict = True
                    break
            if not has_conflict:
                alternatives.append(course)
    
    return alternatives
```

#### Frontend (SchedulerPage.js)
```javascript
// Khi chọn môn học, tự động lấy tất cả sessions
const handleSubjectToggle = async (course) => {
  // Lấy original_code (nếu là session) hoặc code (nếu là môn gốc)
  const originalCode = course.metadata?.original_code || course.code;
  
  // Lấy tất cả sessions từ API
  const response = await api.get(`/api/courses/${originalCode}/sessions`, {
    params: { semester: studyInfo.semester }
  });
  
  // Thêm tất cả sessions vào selectedSubjects
  const sessions = response.data.sessions || [];
  setSelectedSubjects(prev => [
    ...prev,
    ...sessions.map(session => buildSubjectFromSession(session))
  ]);
};
```

### 4. Ưu tiên chọn session thay thế

1. **Ưu tiên sessions trong available_slots** (thời gian rảnh)
2. **Ưu tiên sessions không trùng với môn khác**
3. **Ưu tiên sessions có preferred_days** (nếu có)
4. **Ưu tiên sessions sáng hơn** (nếu preferMorning = true)

### 5. Thông báo cho người dùng

Khi tự động thay thế session:
- Hiển thị màu xanh: "✅ Đã tự động chuyển INT1003-G01 → INT1003-G05"
- Hiển thị lý do: "Để tránh trùng với ACC3001"

Khi không tìm thấy session thay thế:
- Hiển thị màu đỏ: "⚠️ Đã loại bỏ INT1003 (không tìm thấy session thay thế)"

## Lợi ích

1. **Giảm số môn bị loại bỏ**: Từ 8 môn → có thể chỉ còn 1-2 môn
2. **Tự động hóa**: Không cần người dùng can thiệp
3. **Tối ưu**: Vẫn đảm bảo không trùng lịch
4. **Linh hoạt**: Có thể chọn session phù hợp nhất

## Các bước triển khai

1. ✅ Tạo nhiều sessions cho mỗi môn học (add_sample_courses.py)
2. ⏳ Cập nhật API để tự động tìm sessions thay thế
3. ⏳ Cập nhật frontend để tự động lấy tất cả sessions khi chọn môn
4. ⏳ Hiển thị thông báo về sessions đã được thay thế

