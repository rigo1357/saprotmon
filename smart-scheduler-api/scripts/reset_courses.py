"""
Script xoá toàn bộ môn học hiện có và thêm lại dữ liệu mẫu với metadata đầy đủ
Chạy:  python scripts/reset_courses.py
"""
import asyncio
from pathlib import Path
import sys

# Cho phép import db/* khi chạy trực tiếp
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import init_db
from db.models import Course
from scripts.add_sample_courses import add_sample_courses


async def reset_courses():
    await init_db()

    print("🧹 Đang xoá toàn bộ Course hiện có ...")
    delete_result = await Course.find_all().delete()
    deleted = getattr(delete_result, "deleted_count", delete_result)
    print(f"✅ Đã xoá {deleted} lớp học.")

    print("\n🚀 Đang thêm lại dữ liệu mẫu với đầy đủ thông tin (day/start/end/...) ...\n")
    await add_sample_courses()


if __name__ == "__main__":
    asyncio.run(reset_courses())
"""
Script để:
1) XÓA TOÀN BỘ dữ liệu môn học (collection 'courses')
2) Sau đó GẦN GIỐNG như chạy lại add_sample_courses để tạo lại dữ liệu mẫu

Cách dùng (chạy trong thư mục smart-scheduler-api):
    python scripts/reset_courses.py
"""

import asyncio
from pathlib import Path
import sys

# Thêm thư mục gốc vào path để import
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import init_db
from db.models import Course
from scripts.add_sample_courses import add_sample_courses


async def reset_courses():
    print("🚀 Bắt đầu RESET dữ liệu môn học (courses)...")
    await init_db()

    # Xóa toàn bộ collection courses
    deleted_result = await Course.find_all().delete()
    print(f"🗑️ Đã xóa toàn bộ courses, documents bị xóa: {deleted_result}")

    # Tạo lại dữ liệu mẫu với đầy đủ thông tin (bao gồm 'day')
    print("\n📦 Đang tạo lại dữ liệu mẫu bằng add_sample_courses.py ...\n")
    await add_sample_courses()

    print("\n✅ RESET hoàn tất.")


if __name__ == "__main__":
    asyncio.run(reset_courses())


