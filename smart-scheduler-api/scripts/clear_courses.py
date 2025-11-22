"""
Xóa toàn bộ dữ liệu môn học (Course) trong database.

Cách chạy:
    python scripts/clear_courses.py
"""
import asyncio
from pathlib import Path
import sys

# Đảm bảo có thể import được modules trong dự án
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.database import init_db  # noqa: E402
from db.models import Course  # noqa: E402


async def main():
    await init_db()
    result = await Course.delete_all()
    deleted = getattr(result, "deleted_count", None)
    print(f"🗑️  Đã xóa {deleted if deleted is not None else '0'} record trong collection Course.")


if __name__ == "__main__":
    asyncio.run(main())

