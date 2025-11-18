# Giải pháp Tự động Xếp Lại Môn Học Bị Trùng

## Vấn đề
Hiện tại khi các môn học bị trùng lịch, hệ thống chỉ loại bỏ môn học đó. Cần tự động tìm các sessions (nhóm/lớp) khác của cùng môn học để thay thế.

## Giải pháp

### Bước 1: Cập nhật API để tự động tìm sessions thay thế

Trong `main.py`, cập nhật logic xử lý trùng lịch:

```python
async def find_alternative_sessions_from_db(original_code: str, semester: str, 
                                           conflicting_with: dict, 
                                           all_active_entries: list):
    """Tìm sessions thay thế từ database"""
    # Query tất cả sessions của cùng môn học
    courses = await Course.find({
        "metadata.original_code": original_code,
        "semester": semester
    }).to_list()
    
    alternatives = []
    for course in courses:
        # Lấy thông tin session từ metadata
        if not course.metadata or "start_date" not in course.metadata:
            continue
            
        session_entry = {
            "data": type('SubjectInput', (), {
                "name": course.name,
                "code": course.code,
                "start_time": course.metadata.get("start_time", "07:00"),
                "end_time": course.metadata.get("end_time", "11:30"),
                "start_date": course.metadata.get("start_date"),
                "end_date": course.metadata.get("end_date"),
                "credits": course.credits,
                "instructor": course.department or "",
                "subject_type": "Lý thuyết",
                "is_retake": False,
                "priority": 5,
            })(),
            "priority": 5,
            "start": parse_date(course.metadata.get("start_date")),
            "end": parse_date(course.metadata.get("end_date")),
            "original_index": 999,  # Sessions thay thế có index cao
        }
        
        # Kiểm tra không trùng với môn đang conflict
        if not conflicts_with_entry(session_entry, conflicting_with):
            # Kiểm tra không trùng với các môn khác
            has_conflict = False
            for active_entry in all_active_entries:
                if conflicts_with_entry(session_entry, active_entry):
                    has_conflict = True
                    break
            if not has_conflict:
                alternatives.append(session_entry)
    
    return alternatives
```

### Bước 2: Cập nhật logic xử lý trùng lịch

Trong hàm `handle_schedule`, trước khi loại bỏ môn học:

```python
# TRƯỚC KHI LOẠI BỎ: Thử tìm alternative session từ database
remove_code = getattr(remove_entry["data"], "code", "")
original_code = None

# Nếu là session (có -G trong code), lấy original_code
if "-G" in remove_code:
    original_code = remove_code.split("-G")[0]
else:
    # Nếu không phải session, dùng code làm original_code
    original_code = remove_code

if original_code:
    # Tìm sessions thay thế từ database
    alternatives = await find_alternative_sessions_from_db(
        original_code,
        input.semester or "2024-2",  # Lấy từ input hoặc mặc định
        keep_entry,
        active_entries
    )
    
    if alternatives:
        # Chọn session tốt nhất (ưu tiên available_slots)
        best_alternative = None
        for alt in alternatives:
            # Kiểm tra xem session có trong available_slots không
            alt_day = alt["data"].metadata.get("day", "T2")
            alt_time = alt["data"].metadata.get("start_time", "07:00")
            # Map time to slot (Sáng/Chiều/Tối)
            slot = map_time_to_slot(alt_day, alt_time)
            if slot in available_slots:
                best_alternative = alt
                break
        
        if not best_alternative:
            best_alternative = alternatives[0]  # Chọn session đầu tiên
        
        # Thay thế
        remove_entry_index = active_entries.index(remove_entry)
        active_entries[remove_entry_index] = best_alternative
        
        alternative_sessions_used.append({
            "original": remove_entry["data"].name,
            "alternative": best_alternative["data"].name,
            "original_time": f"{remove_entry['data'].start_date} - {remove_entry['data'].end_date}",
            "alternative_time": f"{best_alternative['data'].start_date} - {best_alternative['data'].end_date}",
            "reason": f"Đã tự động chuyển sang nhóm/lớp khác để tránh trùng với {keep_entry['data'].name}"
        })
        continue  # Tiếp tục kiểm tra conflicts
```

### Bước 3: Cập nhật Frontend để tự động lấy tất cả sessions

Trong `SchedulerPage.js`:

```javascript
const handleSubjectToggle = async (course) => {
  setSelectedSubjects(prev => {
    const exists = prev.find(item => {
      // Kiểm tra xem đã có môn học này chưa (theo original_code)
      const itemOriginalCode = item.code.split("-G")[0];
      const courseOriginalCode = course.metadata?.original_code || course.code.split("-G")[0];
      return itemOriginalCode === courseOriginalCode;
    });
    
    if (exists) {
      // Xóa tất cả sessions của môn học này
      const originalCode = course.metadata?.original_code || course.code.split("-G")[0];
      return prev.filter(item => {
        const itemOriginalCode = item.code.split("-G")[0];
        return itemOriginalCode !== originalCode;
      });
    }
    
    // Lấy tất cả sessions của môn học này
    const originalCode = course.metadata?.original_code || course.code.split("-G")[0];
    
    // Gọi API để lấy tất cả sessions
    api.get(`/api/courses/${originalCode}/sessions`, {
      params: { semester: studyInfo.semester }
    }).then(response => {
      const sessions = response.data.sessions || [];
      const isRetake = selectedTab === 'retake';
      
      // Thêm tất cả sessions vào selectedSubjects
      const newSubjects = sessions.map(session => ({
        code: session.code,
        name: session.name,
        displayName: session.name,
        credits: session.credits,
        instructor: session.department || '',
        start_time: session.start_time || '07:00',
        end_time: session.end_time || '11:30',
        start_date: session.start_date,
        end_date: session.end_date,
        subject_type: 'Lý thuyết',
        is_retake: isRetake,
      }));
      
      setSelectedSubjects(prev => [...prev, ...newSubjects]);
    }).catch(error => {
      console.error('Lỗi lấy sessions:', error);
      // Fallback: chỉ thêm môn học hiện tại
      const isRetake = selectedTab === 'retake';
      return [...prev, { ...buildSubjectPayload(course), is_retake: isRetake }];
    });
    
    return prev; // Tạm thời return prev, sẽ update sau khi API call
  });
};
```

## Kết quả mong đợi

1. **Giảm số môn bị loại bỏ**: Từ 8 môn → có thể chỉ còn 1-2 môn
2. **Tự động hóa**: Không cần người dùng can thiệp
3. **Thông báo rõ ràng**: Hiển thị các môn đã được tự động thay thế

## File cần cập nhật

1. `smart-scheduler-api/main.py` - Thêm logic tự động tìm sessions thay thế
2. `smart-scheduler-ui/src/pages/SchedulerPage.js` - Tự động lấy tất cả sessions khi chọn môn
3. `smart-scheduler-api/scripts/add_sample_courses.py` - ✅ Đã hoàn thành (tạo 20-21 sessions)

