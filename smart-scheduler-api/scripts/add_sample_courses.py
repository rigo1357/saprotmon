"""
Script để thêm môn học mẫu cho các ngành khác nhau.
Chạy script này để populate database với dữ liệu mẫu.

Cách sử dụng:
    python scripts/add_sample_courses.py
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Thêm thư mục gốc vào path để import
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import init_db
from db.models import Course, User
from uuid import uuid4

# Dữ liệu môn học mẫu cho các ngành khác nhau
SAMPLE_COURSES = {
    "2024-1": {
        "CNTT": [
            {"code": "INT1001", "name": "Giới thiệu Công nghệ Thông tin", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT1002", "name": "Lập trình Cơ bản", "credits": 4, "department": "Khoa CNTT"},
            {"code": "INT2001", "name": "Cấu trúc Dữ liệu và Giải thuật", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT2002", "name": "Lập trình Hướng đối tượng", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT3001", "name": "Cơ sở Dữ liệu", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT3002", "name": "Mạng Máy tính", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT4001", "name": "Phát triển Ứng dụng Web", "credits": 4, "department": "Khoa CNTT"},
            {"code": "INT4002", "name": "Trí tuệ Nhân tạo", "credits": 3, "department": "Khoa CNTT"},
        ],
        "KT": [
            {"code": "ACC1001", "name": "Nguyên lý Kế toán", "credits": 3, "department": "Khoa Kế toán"},
            {"code": "ACC2001", "name": "Kế toán Tài chính", "credits": 4, "department": "Khoa Kế toán"},
            {"code": "ACC2002", "name": "Kế toán Quản trị", "credits": 3, "department": "Khoa Kế toán"},
            {"code": "FIN1001", "name": "Tài chính Doanh nghiệp", "credits": 3, "department": "Khoa Tài chính"},
            {"code": "FIN2001", "name": "Đầu tư Tài chính", "credits": 3, "department": "Khoa Tài chính"},
            {"code": "MGT1001", "name": "Quản trị Học", "credits": 3, "department": "Khoa Quản trị"},
            {"code": "MGT2001", "name": "Quản trị Nhân sự", "credits": 3, "department": "Khoa Quản trị"},
            {"code": "MGT2002", "name": "Quản trị Marketing", "credits": 3, "department": "Khoa Quản trị"},
        ],
        "NN": [
            {"code": "ENG1001", "name": "Tiếng Anh Cơ bản", "credits": 2, "department": "Khoa Ngoại ngữ"},
            {"code": "ENG2001", "name": "Kỹ năng Giao tiếp", "credits": 2, "department": "Khoa Ngoại ngữ"},
            {"code": "ENG2002", "name": "Tiếng Anh Thương mại", "credits": 3, "department": "Khoa Ngoại ngữ"},
            {"code": "JPN1001", "name": "Tiếng Nhật Cơ bản", "credits": 3, "department": "Khoa Ngoại ngữ"},
            {"code": "CHN1001", "name": "Tiếng Trung Cơ bản", "credits": 3, "department": "Khoa Ngoại ngữ"},
            {"code": "KOR1001", "name": "Tiếng Hàn Cơ bản", "credits": 3, "department": "Khoa Ngoại ngữ"},
        ],
        "TOAN": [
            {"code": "MAT1010", "name": "Giải tích 1", "credits": 4, "department": "Khoa Toán"},
            {"code": "MAT1020", "name": "Đại số Tuyến tính", "credits": 3, "department": "Khoa Toán"},
            {"code": "MAT2010", "name": "Giải tích 2", "credits": 4, "department": "Khoa Toán"},
            {"code": "MAT2020", "name": "Xác suất Thống kê", "credits": 3, "department": "Khoa Toán"},
            {"code": "MAT3010", "name": "Phương trình Vi phân", "credits": 3, "department": "Khoa Toán"},
            {"code": "MAT3020", "name": "Toán Rời rạc", "credits": 3, "department": "Khoa Toán"},
        ],
        "VATLY": [
            {"code": "PHY1001", "name": "Vật lý Đại cương 1", "credits": 3, "department": "Khoa Vật lý"},
            {"code": "PHY1002", "name": "Vật lý Đại cương 2", "credits": 3, "department": "Khoa Vật lý"},
            {"code": "PHY2001", "name": "Cơ học Lượng tử", "credits": 3, "department": "Khoa Vật lý"},
            {"code": "PHY2002", "name": "Điện từ học", "credits": 3, "department": "Khoa Vật lý"},
        ],
        "HOA": [
            {"code": "CHE1001", "name": "Hóa học Đại cương", "credits": 3, "department": "Khoa Hóa học"},
            {"code": "CHE2001", "name": "Hóa học Hữu cơ", "credits": 3, "department": "Khoa Hóa học"},
            {"code": "CHE2002", "name": "Hóa học Vô cơ", "credits": 3, "department": "Khoa Hóa học"},
        ],
    },
    "2024-2": {
        "CNTT": [
            {"code": "INT1003", "name": "Hệ điều hành", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT2003", "name": "Lập trình Web", "credits": 4, "department": "Khoa CNTT"},
            {"code": "INT3003", "name": "An toàn Thông tin", "credits": 3, "department": "Khoa CNTT"},
            {"code": "INT4003", "name": "Machine Learning", "credits": 3, "department": "Khoa CNTT"},
        ],
        "KT": [
            {"code": "ACC3001", "name": "Kiểm toán", "credits": 3, "department": "Khoa Kế toán"},
            {"code": "FIN3001", "name": "Quản trị Rủi ro", "credits": 3, "department": "Khoa Tài chính"},
        ],
    }
}

SESSIONS_PER_COURSE = 1

def generate_sessions_for_course(semester, num_sessions=SESSIONS_PER_COURSE):
    """
    Tạo nhiều sessions cho một môn học với các thời gian khác nhau.
    Mỗi session có cùng code, cùng tên môn nhưng khác thời gian học.
    """
    sessions = []
    
    # Xác định khoảng thời gian học kỳ
    # Giả sử học kỳ bắt đầu từ tháng 9 (nếu 2024-1) hoặc tháng 2 (nếu 2024-2)
    if semester.endswith("-1"):
        # Học kỳ 1: tháng 9 - tháng 12
        base_date = datetime(2024, 9, 1)
        end_date = datetime(2024, 12, 31)
    elif semester.endswith("-2"):
        # Học kỳ 2: tháng 2 - tháng 5
        base_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 5, 31)
    else:
        # Mặc định
        base_date = datetime(2024, 9, 1)
        end_date = datetime(2024, 12, 31)
    
    # Các khung giờ học
    time_slots = [
        {"start": "07:00", "end": "09:30", "label": "Sáng sớm"},
        {"start": "07:30", "end": "10:00", "label": "Sáng"},
        {"start": "08:00", "end": "10:30", "label": "Sáng"},
        {"start": "09:00", "end": "11:30", "label": "Sáng"},
        {"start": "10:00", "end": "12:30", "label": "Sáng muộn"},
        {"start": "12:30", "end": "15:00", "label": "Chiều sớm"},
        {"start": "13:00", "end": "15:30", "label": "Chiều"},
        {"start": "13:30", "end": "16:00", "label": "Chiều"},
        {"start": "14:00", "end": "16:30", "label": "Chiều"},
        {"start": "15:00", "end": "17:30", "label": "Chiều muộn"},
        {"start": "17:30", "end": "20:00", "label": "Tối sớm"},
        {"start": "18:00", "end": "20:30", "label": "Tối"},
        {"start": "18:30", "end": "21:00", "label": "Tối"},
        {"start": "19:00", "end": "21:30", "label": "Tối muộn"},
    ]
    
    # Các ngày trong tuần
    days_of_week = ["T2", "T3", "T4", "T5", "T6", "T7"]
    
    # Tạo các sessions với thời gian khác nhau
    session_count = 0
    used_combinations = set()
    
    while session_count < num_sessions:
        # Chọn ngẫu nhiên một ngày trong tuần
        day = random.choice(days_of_week)
        
        # Chọn ngẫu nhiên một khung giờ
        time_slot = random.choice(time_slots)
        
        # Tạo một ngày học cụ thể trong học kỳ
        # Chọn ngẫu nhiên một tuần trong học kỳ (tuần 1-15)
        week_offset = random.randint(0, 14)
        session_date = base_date + timedelta(weeks=week_offset)
        
        # Điều chỉnh ngày theo ngày trong tuần
        # T2 = 0, T3 = 1, ..., T7 = 5
        day_offset = days_of_week.index(day)
        session_date = session_date + timedelta(days=day_offset - session_date.weekday())
        
        # Đảm bảo ngày nằm trong khoảng học kỳ
        if session_date < base_date:
            session_date = base_date + timedelta(days=day_offset)
        if session_date > end_date:
            continue
        
        # Tạo ngày kết thúc (thường là 15 tuần sau)
        end_session_date = session_date + timedelta(weeks=15)
        if end_session_date > end_date:
            end_session_date = end_date
        
        # Tạo key để tránh trùng lặp
        combination_key = (day, time_slot["start"], time_slot["end"])
        if combination_key in used_combinations:
            continue
        
        used_combinations.add(combination_key)
        
        sessions.append({
            "day": day,
            "start_time": time_slot["start"],
            "end_time": time_slot["end"],
            "start_date": session_date.strftime("%Y-%m-%d"),
            "end_date": end_session_date.strftime("%Y-%m-%d"),
            "label": time_slot["label"],
            "group": f"Nhóm {session_count + 1}",
        })
        
        session_count += 1
    
    return sessions

async def add_sample_courses():
    """Thêm môn học mẫu vào database với nhiều sessions cho mỗi môn."""
    await init_db()
    
    # Lấy admin user đầu tiên làm created_by
    admin_user = await User.find_one({"is_admin": True})
    if not admin_user:
        print("⚠️  Không tìm thấy admin user. Vui lòng tạo admin trước.")
        return
    
    total_added = 0
    total_sessions = 0
    
    for semester, majors in SAMPLE_COURSES.items():
        for major, courses in majors.items():
            for course_data in courses:
                # Chỉ tạo đúng số sessions cấu hình (mặc định 1)
                num_sessions = SESSIONS_PER_COURSE
                sessions = generate_sessions_for_course(semester, num_sessions)
                
                # Tạo một Course record cho mỗi session
                for session_idx, session in enumerate(sessions):
                    # Tạo code duy nhất cho mỗi session (thêm suffix)
                    session_code = f"{course_data['code']}-G{session_idx + 1:02d}"
                    
                    # Kiểm tra xem session đã tồn tại chưa
                    existing = await Course.find_one({
                        "code": session_code,
                        "semester": semester,
                        "major": major
                    })
                    
                    if existing:
                        print(f"⏭️  Đã tồn tại: {session_code} - {course_data['name']} ({semester}, {major})")
                        continue
                    
                    # Tạo môn học mới với thông tin session
                    new_course = Course(
                        code=session_code,
                        name=course_data["name"],
                        credits=course_data["credits"],
                        semester=semester,
                        department=course_data.get("department", ""),
                        major=major,
                        created_by=admin_user.id,
                        metadata={
                            "original_code": course_data["code"],  # Lưu code gốc để dễ tìm
                            "session_info": session,  # Lưu thông tin session
                            "group": session["group"],
                            "day": session["day"],
                            "start_time": session["start_time"],
                            "end_time": session["end_time"],
                            "start_date": session["start_date"],
                            "end_date": session["end_date"],
                        }
                    )
                    
                    await new_course.save()
                    total_added += 1
                    total_sessions += 1
                
                print(f"✅ Đã thêm {num_sessions} session cho: {course_data['code']} - {course_data['name']} ({semester}, {major})")
    
    print(f"\n🎉 Hoàn thành! Đã thêm {total_added} môn học (sessions) mới.")
    print(f"📊 Tổng số sessions: {total_sessions}")
    print(f"\n📋 Danh sách môn học theo ngành:")
    for semester, majors in SAMPLE_COURSES.items():
        print(f"\n  Học kỳ {semester}:")
        for major, courses in majors.items():
            total_sessions_for_major = len(courses) * SESSIONS_PER_COURSE
            print(f"    - {major}: {len(courses)} môn, {total_sessions_for_major} session")

if __name__ == "__main__":
    print("🚀 Bắt đầu thêm môn học mẫu...\n")
    asyncio.run(add_sample_courses())

