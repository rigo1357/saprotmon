# smart-scheduler-api/db/models.py
from beanie import Document
from pydantic import Field, EmailStr
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime # Thêm import này

# =================
# Model Người Dùng
# =================
class User(Document):
    id: UUID = Field(default_factory=uuid4)
    full_name: str = Field(default="")  # Họ và tên
    username: str
    email: Optional[str] = None  # Dùng str thay vì EmailStr để linh hoạt hơn
    phone: Optional[str] = None  # Số điện thoại
    hashed_password: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)  # Thêm created_at
    
    class Settings:
        name = "users"

# =================
# Model Lịch Học
# =================
class Schedule(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # Để liên kết với User đã tạo ra nó
    created_at: datetime = Field(default_factory=datetime.now) # Dùng datetime
    
    schedule_data: List[Dict[str, Any]]
    cost: float
    
    class Settings:
        name = "schedules"

# =================
# Model Môn học
# =================
class Course(Document):
    id: UUID = Field(default_factory=uuid4)
    code: str
    name: str
    credits: int = 0
    semester: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "courses"

# =================
# Model Lịch sử Chat
# =================
class ChatHistory(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # Người dùng
    session_id: str  # ID phiên chat (để nhóm các tin nhắn)
    message: str  # Nội dung tin nhắn
    role: str  # "user" hoặc "assistant"
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "chat_history"

# =================
# Model OTP (Mã xác thực)
# =================
class OTP(Document):
    id: UUID = Field(default_factory=uuid4)
    identifier: str  # Email hoặc số điện thoại
    otp_code: str  # Mã OTP (6 chữ số)
    purpose: str  # "forgot_password" hoặc "verify_account"
    expires_at: datetime  # Thời gian hết hạn (15 phút)
    is_used: bool = False  # Đã sử dụng chưa
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "otps"