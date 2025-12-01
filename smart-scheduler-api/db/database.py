# smart-scheduler-api/db/database.py
import os
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from .models import User, Schedule, Course, ChatHistory, OTP

# Global client để tái sử dụng
_client = None

# Load .env file nếu có
def load_env_file():
    """Đọc file .env nếu tồn tại"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value
                        print(f"✓ Đã load từ .env: {key} = {value[:50]}...")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc file .env: {e}")

# Load .env khi import module
load_env_file()

async def init_db():
    global _client
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    print(f"Đang kết nối với MongoDB tại: {mongodb_url[:50]}...")
    
    try:
        _client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            maxPoolSize=50,
            minPoolSize=10,
            retryWrites=True,
            retryReads=True,
        )
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await _client.admin.command('ping')
                print("✓ Kết nối MongoDB thành công!")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Lần thử {attempt + 1} thất bại, thử lại...")
                    await asyncio.sleep(1)
                else:
                    raise
        
        database = _client.smart_scheduler_db

        print("Đang khởi tạo Beanie với MongoDB...")
        
        await init_beanie(
            database=database,
            document_models=[User, Schedule, Course, ChatHistory, OTP]
        )
        print("✓ Khởi tạo Beanie hoàn tất.")
        
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print("=" * 60)
        print("❌ LỖI: Không thể kết nối với MongoDB!")
        print("=" * 60)
        print(f"Chi tiết lỗi: {e}")
        print("\nHướng dẫn khắc phục:")
        print("1. Kiểm tra IP đã được whitelist trong MongoDB Atlas")
        print("2. Kiểm tra connection string trong file .env")
        print("3. Kiểm tra network connection")
        print("4. Thử chạy lại: python check_mongodb.py")
        print("=" * 60)
        raise ConnectionError("MongoDB connection failed.")
    except Exception as e:
        print(f"❌ Lỗi không xác định khi kết nối MongoDB: {e}")
        import traceback
        traceback.print_exc()
        raise