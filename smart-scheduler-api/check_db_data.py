import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from typing import Optional
import sys

# Define Course model matching main.py
class Course(Document):
    code: str
    name: str
    credits: Optional[int] = None
    semester: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    metadata: Optional[dict] = None
    created_by: Optional[str] = None

    class Settings:
        name = "courses"

async def check_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.smart_scheduler
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[Course])
    
    # Check total courses
    total = await Course.count()
    print(f"=== Total Courses: {total} ===\n")
    
    if total == 0:
        print("❌ No courses in database! This is why dropdowns are empty.")
        return
    
    # Check unique semesters
    pipeline = [
        {"$group": {"_id": "$semester"}},
        {"$sort": {"_id": -1}}
    ]
    semesters_result = await Course.get_motor_collection().aggregate(pipeline).to_list(length=None)
    semesters = [r["_id"] for r in semesters_result if r["_id"]]
    
    print(f"=== Unique Semesters ({len(semesters)}): ===")
    for sem in semesters:
        print(f"  - {sem}")
    
    # Check unique majors
    pipeline_majors = [
        {"$group": {"_id": "$major"}},
        {"$sort": {"_id": 1}}
    ]
    majors_result = await Course.get_motor_collection().aggregate(pipeline_majors).to_list(length=None)
    majors = [r["_id"] for r in majors_result if r["_id"]]
    
    print(f"\n=== Unique Majors ({len(majors)}): ===")
    for maj in majors:
        print(f"  - {maj}")
    
    # Check course names for encoding issues
    print(f"\n=== Checking First 5 Courses for Encoding Issues ===")
    courses = await Course.find().limit(5).to_list()
    for course in courses:
        # Try to encode/decode to check for issues
        try:
            encoded = course.name.encode('utf-8')
            decoded = encoded.decode('utf-8')
            status = "✓ OK" if course.name == decoded else "❌ ENCODING ISSUE"
        except Exception as e:
            status = f"❌ ERROR: {e}"
        
        print(f"{course.code}: {course.name}")
        print(f"  Status: {status}")
        print(f"  Bytes: {course.name.encode('utf-8', errors='replace')[:50]}")
        print()

if __name__ == "__main__":
    asyncio.run(check_data())
