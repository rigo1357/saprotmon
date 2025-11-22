# smart-scheduler-api/schemas.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime

# --- Khuôn cho User ---
class UserCreate(BaseModel):
    full_name: str  # Họ và tên (bắt buộc)
    username: str  # Tên đăng nhập (bắt buộc)
    password: str  # Mật khẩu (bắt buộc)
    confirm_password: str  # Xác nhận mật khẩu (bắt buộc)
    email: Optional[str] = None  # Email (tùy chọn)
    phone: Optional[str] = None  # Số điện thoại (tùy chọn)
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        """Xử lý email rỗng - chuyển thành None"""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        """Xử lý phone rỗng - chuyển thành None"""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_passwords_match(cls, v, info):
        """Kiểm tra mật khẩu xác nhận khớp"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v

# --- Khuôn cho Token (Login) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[str] = None

# --- Khuôn cho Chatbot ---
class ChatInput(BaseModel):
    message: str
    session_id: Optional[str] = None  # ID phiên chat (để nhóm các tin nhắn)

class ChatMessage(BaseModel):
    role: str  # "user" hoặc "assistant"
    content: str
    created_at: Optional[datetime] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime

class ChatSearchResponse(BaseModel):
    total: int
    sessions: List[ChatHistoryResponse]

# --- Khuôn cho Môn học ---
class SubjectInput(BaseModel):
    name: str  # Tên môn học
    start_time: str  # Thời gian bắt đầu (ví dụ: "08:00")
    end_time: str  # Thời gian kết thúc (ví dụ: "10:00")
    credits: int  # Số tín chỉ
    subject_type: str  # "Thực hành" hoặc "Lý thuyết"
    instructor: str  # Tên giảng viên
    start_date: str  # Ngày bắt đầu học (format: "YYYY-MM-DD")
    end_date: str  # Ngày kết thúc học (format: "YYYY-MM-DD")
    day: Optional[Union[str, List[str]]] = None  # Ngày học (VD: "T2" hoặc ["T2","T4"])
    priority: int = Field(default=5, ge=1, le=10)  # Độ ưu tiên (1-10, 10 là cao nhất)
    is_retake: Optional[bool] = False  # Đánh dấu môn học lại
    preferred_days: Optional[List[str]] = Field(default=None)  # Ưu tiên ngày học (VD: ["T2", "T3"])

# --- Khuôn cho Thông tin học tập ---
class StudyInfo(BaseModel):
    semester: str
    academicYear: int
    major: str
    maxCredits: int
    minSubjects: int
    maxSubjects: int

# --- Khuôn cho Ràng buộc bổ sung ---
class AdditionalConstraints(BaseModel):
    avoidConsecutive: bool = False  # Tránh xếp các môn học liên tiếp
    balanceDays: bool = False  # Cân bằng số môn học giữa các ngày
    preferMorning: bool = False  # Ưu tiên học buổi sáng
    allowSaturday: bool = False  # Cho phép học thứ 7

# --- Khuôn cho Xếp lịch ---
class ScheduleInput(BaseModel):
    subjects: List[SubjectInput]  # Danh sách môn học
    available_time_slots: List[str] = Field(default=[], example=["T2_Sáng", "T2_Chiều", "T3_Sáng"])  # Các khung giờ có sẵn
    constraints: Dict[str, List[str]] = Field(default={}, example={"Toán": ["T2_Sáng"]})  # Ràng buộc (tên môn -> danh sách giờ cấm)
    additionalConstraints: Optional[AdditionalConstraints] = None  # Ràng buộc bổ sung

# --- Khuôn cho môn học (DB <-> API) ---
class CourseBase(BaseModel):
    code: str
    name: str
    credits: int = 0
    semester: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CourseCreate(CourseBase):
    semester: str  # Bắt buộc khi thêm thủ công

class CourseListResponse(BaseModel):
    total: int
    items: List[CourseBase]

class CourseUploadResponse(BaseModel):
    inserted: int
    semester: Optional[str] = None
    sample: List[CourseBase] = Field(default_factory=list)

# --- Khuôn cho User Response ---
class UserResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_admin: bool
    created_at: Optional[datetime] = None

class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]

# --- Khuôn cho Quên mật khẩu ---
class ForgotPasswordRequest(BaseModel):
    identifier: str  # Email hoặc số điện thoại

class VerifyOTPRequest(BaseModel):
    identifier: str  # Email hoặc số điện thoại
    otp_code: str  # Mã OTP

class ResetPasswordRequest(BaseModel):
    identifier: str  # Email hoặc số điện thoại
    otp_code: str  # Mã OTP đã xác nhận
    new_password: str  # Mật khẩu mới
    confirm_password: str  # Xác nhận mật khẩu mới
    
    @field_validator('confirm_password')
    @classmethod
    def validate_passwords_match(cls, v, info):
        """Kiểm tra mật khẩu xác nhận khớp"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v