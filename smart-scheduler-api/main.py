# smart-scheduler-api/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import pandas as pd
import io
import traceback
import random
import re

from db.database import init_db
from db.models import User, Schedule, Course, ChatHistory, OTP
from schemas import (
    UserCreate, Token, ScheduleInput, SubjectInput,
    CourseBase, CourseCreate, CourseListResponse, CourseUploadResponse,
    ChatInput, ChatMessage, ChatHistoryResponse, ChatSearchResponse,
    UserResponse, UserListResponse,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from auth.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
)
from chatbot.client import get_bot_response
from genetic_algorithm.scheduler_ga import find_optimal_schedule

# =================
# KHỞI TẠO APP
# =================
app = FastAPI(title="Smart Scheduler API", version="1.0.0")

# =================
# CORS CONFIGURATION
# =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================
# KHỞI TẠO DATABASE
# =================
@app.on_event("startup")
async def startup_event():
    await init_db()

# =================
# HELPER FUNCTIONS
# =================
def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except Exception:
        return default

def _dataframe_to_courses(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    df = df.rename(columns={col: col.strip().lower() for col in df.columns})
    alias_map = {
        "mã môn": "code", "mã môn học": "code", "ma mon": "code",
        "ma mon hoc": "code", "course code": "code", "code": "code",
        "ma hp": "code", "mã hp": "code",
        "tên môn": "name", "tên môn học": "name", "ten mon": "name",
        "ten mon hoc": "name", "course name": "name", "name": "name",
        "tín chỉ": "credits", "số tín chỉ": "credits", "so tin chi": "credits",
        "credits": "credits",
        "bộ môn": "department", "department": "department",
    }
    df = df.rename(columns={col: alias_map.get(col, col) for col in df.columns})
    if "code" not in df.columns or "name" not in df.columns:
        raise ValueError("Không tìm thấy cột 'code' hoặc 'name' trong file.")
    courses = []
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        name = str(row.get("name", "")).strip()
        if not code or not name:
            continue
        course = {
            "code": code,
            "name": name,
            "credits": _coerce_int(row.get("credits", 0)),
            "department": str(row.get("department") or "").strip() or None,
        }
        courses.append(course)
    return courses

def _parse_pdf_courses(file_bytes: bytes) -> List[Dict[str, Any]]:
    courses: List[Dict[str, Any]] = []
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    headers = [h.strip().lower() if h else "" for h in table[0]]
                    for row in table[1:]:
                        if not row or len(row) < 2:
                            continue
                        code_idx = next((i for i, h in enumerate(headers) if "mã" in h or "code" in h), 0)
                        name_idx = next((i for i, h in enumerate(headers) if "tên" in h or "name" in h), 1)
                        credits_idx = next((i for i, h in enumerate(headers) if "tín" in h or "credits" in h), 2)
                        code = str(row[code_idx] or "").strip()
                        name = str(row[name_idx] or "").strip()
                        if code and name:
                            courses.append({
                                "code": code,
                                "name": name,
                                "credits": _coerce_int(row[credits_idx] if credits_idx < len(row) else 0),
                                "department": None,
                            })
    except Exception as e:
        print(f"Lỗi parse PDF: {e}")
    return courses

def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    return current_user

# =================
# API AUTHENTICATION
# =================
@app.post("/api/register", status_code=201)
async def register(user_data: UserCreate):
    # Kiểm tra username đã tồn tại
    existing = await User.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    
    # Kiểm tra email hoặc phone đã tồn tại (nếu có)
    if user_data.email:
        existing_email = await User.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
    
    if user_data.phone:
        existing_phone = await User.find_one({"phone": user_data.phone})
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng")
    
    # Hash mật khẩu
    hashed = get_password_hash(user_data.password)
    
    # Tạo user mới
    new_user = User(
        full_name=user_data.full_name,
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed,
        is_admin=False
    )
    await new_user.save()
    return {"message": "Đăng ký thành công", "user_id": str(new_user.id)}

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng")
    access_token = create_access_token(data={"sub": user.username, "id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "full_name": getattr(current_user, 'full_name', ''),
        "username": current_user.username,
        "email": current_user.email,
        "phone": getattr(current_user, 'phone', None),
        "is_admin": current_user.is_admin
    }

# =================
# API QUÊN MẬT KHẨU
# =================
def generate_otp() -> str:
    """Tạo mã OTP 6 chữ số"""
    return str(random.randint(100000, 999999))

def is_email(identifier: str) -> bool:
    """Kiểm tra identifier là email hay số điện thoại"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, identifier))

async def send_otp_email(email: str, otp_code: str):
    """Gửi OTP qua email (tạm thời chỉ log, cần tích hợp email service)"""
    print(f"[EMAIL] Gửi mã OTP đến {email}: {otp_code}")
    # TODO: Tích hợp email service (SMTP, SendGrid, etc.)
    # Ví dụ với SMTP:
    # import smtplib
    # from email.mime.text import MIMEText
    # msg = MIMEText(f"Mã OTP của bạn là: {otp_code}")
    # msg['Subject'] = 'Mã OTP đặt lại mật khẩu'
    # msg['From'] = 'noreply@smart-scheduler.com'
    # msg['To'] = email
    # server.sendmail(...)

async def send_otp_sms(phone: str, otp_code: str):
    """Gửi OTP qua SMS (tạm thời chỉ log, cần tích hợp SMS service)"""
    print(f"[SMS] Gửi mã OTP đến {phone}: {otp_code}")
    # TODO: Tích hợp SMS service (Twilio, AWS SNS, etc.)

@app.post("/api/forgot-password/request")
async def request_password_reset(request: ForgotPasswordRequest):
    """Gửi mã OTP để đặt lại mật khẩu"""
    identifier = request.identifier.strip()
    
    # Tìm user theo email hoặc phone
    if is_email(identifier):
        user = await User.find_one({"email": identifier})
    else:
        user = await User.find_one({"phone": identifier})
    
    if not user:
        # Không tiết lộ user có tồn tại hay không (bảo mật)
        return {
            "message": "Nếu email/số điện thoại tồn tại, mã OTP đã được gửi.",
            "identifier": identifier
        }
    
    # Xóa các OTP cũ chưa dùng của user này
    await OTP.find({
        "identifier": identifier,
        "purpose": "forgot_password",
        "is_used": False
    }).delete()
    
    # Tạo OTP mới
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=15)
    
    new_otp = OTP(
        identifier=identifier,
        otp_code=otp_code,
        purpose="forgot_password",
        expires_at=expires_at,
        is_used=False
    )
    await new_otp.save()
    
    # Gửi OTP
    if is_email(identifier):
        await send_otp_email(identifier, otp_code)
    else:
        await send_otp_sms(identifier, otp_code)
    
    return {
        "message": "Mã OTP đã được gửi. Vui lòng kiểm tra email/số điện thoại của bạn.",
        "identifier": identifier,
        "expires_in_minutes": 15
    }

@app.post("/api/forgot-password/verify")
async def verify_otp(request: VerifyOTPRequest):
    """Xác nhận mã OTP"""
    identifier = request.identifier.strip()
    otp_code = request.otp_code.strip()
    
    # Tìm OTP hợp lệ
    otp = await OTP.find_one({
        "identifier": identifier,
        "otp_code": otp_code,
        "purpose": "forgot_password",
        "is_used": False
    })
    
    if not otp:
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc đã hết hạn")
    
    if otp.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới.")
    
    return {
        "message": "Mã OTP hợp lệ. Bạn có thể đặt lại mật khẩu.",
        "verified": True
    }

@app.post("/api/forgot-password/reset")
async def reset_password(request: ResetPasswordRequest):
    """Đặt lại mật khẩu sau khi xác nhận OTP"""
    identifier = request.identifier.strip()
    otp_code = request.otp_code.strip()
    
    # Xác nhận OTP
    otp = await OTP.find_one({
        "identifier": identifier,
        "otp_code": otp_code,
        "purpose": "forgot_password",
        "is_used": False
    })
    
    if not otp:
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ")
    
    if otp.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
    
    # Tìm user
    if is_email(identifier):
        user = await User.find_one({"email": identifier})
    else:
        user = await User.find_one({"phone": identifier})
    
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    # Cập nhật mật khẩu
    user.hashed_password = get_password_hash(request.new_password)
    await user.save()
    
    # Đánh dấu OTP đã sử dụng
    otp.is_used = True
    await otp.save()
    
    return {
        "message": "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập với mật khẩu mới."
    }

# =================
# API CHATBOT
# =================
@app.post("/api/chat")
async def handle_chat(
    input: ChatInput,
    current_user: User = Depends(get_current_user)
):
    session_id = input.session_id or str(uuid4())
    
    try:
        # Lưu tin nhắn của user
        user_message = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            message=input.message,
            role="user"
        )
        await user_message.save()
    except Exception as e:
        print(f"Lỗi lưu tin nhắn user: {e}")
        traceback.print_exc()
        # Vẫn tiếp tục, không fail nếu không lưu được
    
    try:
        # Lấy lịch sử chat trong session này để context
        previous_messages = await ChatHistory.find(
            {"session_id": session_id, "user_id": current_user.id}
        ).sort("created_at").to_list()
        
        # Tạo context từ lịch sử
        context_messages = []
        for msg in previous_messages[-10:]:  # Chỉ lấy 10 tin nhắn gần nhất
            context_messages.append({
                "role": msg.role,
                "content": msg.message
            })
        
        # Gọi chatbot với context (bỏ tin nhắn user cuối cùng vì đã lưu rồi)
        if len(context_messages) > 1:  # Có lịch sử (có ít nhất 2 tin nhắn: user và assistant)
            # Bỏ tin nhắn user cuối cùng (đã lưu ở trên)
            reply = await get_bot_response(input.message, context_messages[:-1])
        else:
            reply = await get_bot_response(input.message, [])
        
        # Lưu phản hồi của bot
        try:
            bot_message = ChatHistory(
                user_id=current_user.id,
                session_id=session_id,
                message=reply,
                role="assistant"
            )
            await bot_message.save()
        except Exception as e:
            print(f"Lỗi lưu tin nhắn bot: {e}")
            # Vẫn trả về reply nếu không lưu được
        
        return {"reply": reply, "session_id": session_id}
        
    except HTTPException:
        # Re-raise HTTPException để giữ nguyên status code
        raise
    except Exception as e:
        print(f"Lỗi chatbot: {e}")
        traceback.print_exc()
        
        # Trả về message lỗi thân thiện thay vì raise HTTPException
        error_message = "Xin lỗi, tôi đang gặp sự cố khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        
        # Kiểm tra loại lỗi cụ thể
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str or "connect" in error_str:
            error_message = "Xin lỗi, tôi không thể kết nối với mô hình AI. Vui lòng kiểm tra Ollama đã được khởi động chưa (chạy 'ollama serve' trong terminal)."
        elif "timeout" in error_str:
            error_message = "Xin lỗi, yêu cầu đã hết thời gian chờ. Vui lòng thử lại."
        elif "model" in error_str or "not found" in error_str:
            error_message = "Xin lỗi, mô hình AI chưa được tải. Vui lòng chạy 'ollama pull gemma2:9b' hoặc 'ollama pull gemma2:2b' trong terminal."
        
        # Lưu message lỗi vào database (nếu có thể)
        try:
            bot_message = ChatHistory(
                user_id=current_user.id,
                session_id=session_id,
                message=error_message,
                role="assistant"
            )
            await bot_message.save()
        except:
            pass
        
        return {"reply": error_message, "session_id": session_id}

@app.get("/api/chat/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(current_user: User = Depends(get_current_user)):
    messages = await ChatHistory.find({"user_id": current_user.id}).sort("created_at").to_list()
    sessions_dict = {}
    for msg in messages:
        if msg.session_id not in sessions_dict:
            sessions_dict[msg.session_id] = {
                "session_id": msg.session_id,
                "messages": [],
                "created_at": msg.created_at
            }
        sessions_dict[msg.session_id]["messages"].append(
            ChatMessage(role=msg.role, content=msg.message, created_at=msg.created_at)
        )
    return [ChatHistoryResponse(**session) for session in sessions_dict.values()]

@app.get("/api/chat/search", response_model=ChatSearchResponse)
async def search_chat_history(
    q: str,
    current_user: User = Depends(get_current_user)
):
    messages = await ChatHistory.find({
        "user_id": current_user.id,
        "message": {"$regex": q, "$options": "i"}
    }).sort("created_at").to_list()
    sessions_dict = {}
    for msg in messages:
        if msg.session_id not in sessions_dict:
            sessions_dict[msg.session_id] = {
                "session_id": msg.session_id,
                "messages": [],
                "created_at": msg.created_at
            }
        sessions_dict[msg.session_id]["messages"].append(
            ChatMessage(role=msg.role, content=msg.message, created_at=msg.created_at)
        )
    return ChatSearchResponse(
        total=len(sessions_dict),
        sessions=[ChatHistoryResponse(**session) for session in sessions_dict.values()]
    )

@app.delete("/api/chat/history/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    deleted = await ChatHistory.find({
        "user_id": current_user.id,
        "session_id": session_id
    }).delete()
    return {"deleted": deleted}

# =================
# API COURSES
# =================
@app.get("/api/courses/{course_code}/sessions")
async def get_course_sessions(
    course_code: str,
    semester: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Lấy tất cả các sessions (nhóm/lớp) của một môn học."""
    # Nếu course_code có -G, lấy original_code
    if "-G" in course_code:
        original_code = course_code.split("-G")[0]
    else:
        original_code = course_code
    
    query = {"metadata.original_code": original_code}
    if semester:
        query["semester"] = semester
    
    courses = await Course.find(query).sort("code").to_list()
    
    sessions = []
    for course in courses:
        if course.metadata:
            sessions.append({
                "code": course.code,
                "name": course.name,
                "credits": course.credits,
                "semester": course.semester,
                "department": course.department,
                "major": course.major,
                "session_info": course.metadata.get("session_info", {}),
                "start_date": course.metadata.get("start_date"),
                "end_date": course.metadata.get("end_date"),
                "start_time": course.metadata.get("start_time", "07:00"),
                "end_time": course.metadata.get("end_time", "11:30"),
                "day": course.metadata.get("day"),
                "group": course.metadata.get("group"),
                "original_code": course.metadata.get("original_code", original_code),
            })
    
    return {"total": len(sessions), "sessions": sessions}

@app.get("/api/courses", response_model=CourseListResponse)
async def list_courses(
    semester: Optional[str] = None,
    major: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách môn học hiện có (đã upload)."""
    query: Dict[str, Any] = {}
    if semester:
        query["semester"] = semester
    if major:
        query["major"] = major

    courses = await Course.find(query).sort("code").to_list()

    return CourseListResponse(
        total=len(courses),
        items=[
            CourseBase(
                code=course.code,
                name=course.name,
                credits=course.credits,
                semester=course.semester,
                department=course.department,
                major=course.major,
                metadata=course.metadata,
            )
            for course in courses
        ],
    )

@app.post("/api/admin/upload-courses", response_model=CourseUploadResponse)
async def upload_courses(
    semester: str = Form(...),
    department: Optional[str] = Form(default=None),
    major: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    current_admin: User = Depends(admin_required),
):
    try:
        file_bytes = await file.read()
        courses = []
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
            courses = _dataframe_to_courses(df)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(file_bytes))
            courses = _dataframe_to_courses(df)
        elif file.filename.endswith('.pdf'):
            courses = _parse_pdf_courses(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ")
        
        inserted = 0
        for course_data in courses:
            existing = await Course.find_one({
                "code": course_data["code"],
                "semester": semester
            })
            if not existing:
                new_course = Course(
                    code=course_data["code"],
                    name=course_data["name"],
                    credits=course_data["credits"],
                    semester=semester,
                    department=course_data.get("department") or department,
                    major=major,
                    created_by=current_admin.id,
                )
                await new_course.save()
                inserted += 1
        
        sample = [CourseBase(**c) for c in courses[:5]]
        return CourseUploadResponse(inserted=inserted, semester=semester, sample=sample)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi upload: {str(e)}")

@app.post("/api/admin/courses", response_model=CourseBase)
async def create_course(
    course: CourseCreate,
    current_admin: User = Depends(admin_required),
):
    existing = await Course.find_one({"code": course.code, "semester": course.semester})
    if existing:
        raise HTTPException(status_code=400, detail=f"Môn học {course.code} đã tồn tại trong học kỳ {course.semester}")
    new_course = Course(
        code=course.code,
        name=course.name,
        credits=course.credits,
        semester=course.semester,
        department=course.department,
        major=course.major,
        created_by=current_admin.id,
    )
    await new_course.save()
    return CourseBase(
        code=new_course.code,
        name=new_course.name,
        credits=new_course.credits,
        semester=new_course.semester,
        department=new_course.department,
        major=new_course.major,
        metadata=new_course.metadata,
    )

# =================
# API QUẢN LÝ NGƯỜI DÙNG (ADMIN)
# =================
@app.get("/api/admin/users", response_model=UserListResponse)
async def list_users(
    current_admin: User = Depends(admin_required),
):
    """Lấy danh sách tất cả người dùng (chỉ admin)."""
    users = await User.find_all().sort("created_at").to_list()
    
    user_list = []
    for user in users:
        user_list.append(UserResponse(
            id=str(user.id),
            full_name=getattr(user, 'full_name', ''),
            username=user.username,
            email=user.email,
            phone=getattr(user, 'phone', None),
            is_admin=user.is_admin,
            created_at=getattr(user, 'created_at', None)
        ))
    
    return UserListResponse(
        total=len(user_list),
        users=user_list
    )

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(admin_required),
):
    """Xóa người dùng (chỉ admin)."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    
    # Không cho phép xóa chính mình
    if user_uuid == current_admin.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính tài khoản của bạn")
    
    user = await User.get(user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    # Xóa tất cả dữ liệu liên quan (schedules, chat history)
    await Schedule.find({"user_id": user_uuid}).delete()
    await ChatHistory.find({"user_id": user_uuid}).delete()
    
    # Xóa user
    await user.delete()
    
    return {"message": "Đã xóa người dùng thành công", "deleted_user_id": user_id}

@app.patch("/api/admin/users/{user_id}/toggle-admin")
async def toggle_admin_status(
    user_id: str,
    current_admin: User = Depends(admin_required),
):
    """Chuyển đổi trạng thái admin của người dùng (chỉ admin)."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    
    # Không cho phép thay đổi chính mình
    if user_uuid == current_admin.id:
        raise HTTPException(status_code=400, detail="Không thể thay đổi quyền admin của chính bạn")
    
    user = await User.get(user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    user.is_admin = not user.is_admin
    await user.save()
    
    return {
        "message": f"Đã {'cấp' if user.is_admin else 'thu hồi'} quyền admin cho {user.username}",
        "user": UserResponse(
            id=str(user.id),
            full_name=getattr(user, 'full_name', ''),
            username=user.username,
            email=user.email,
            phone=getattr(user, 'phone', None),
            is_admin=user.is_admin,
            created_at=getattr(user, 'created_at', None)
        )
    }

# =================
# API SCHEDULE - VỚI TỰ ĐỘNG TÌM SESSIONS THAY THẾ
# =================
@app.post("/api/schedule")
async def handle_schedule(
    input: ScheduleInput,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"Nhận yêu cầu xếp lịch từ user: {current_user.username}")
        print(f"Số môn học: {len(input.subjects)}")
        
        # 1. Chuẩn hóa dữ liệu
        def parse_date(value: str) -> datetime.date:
            return datetime.strptime(value, "%Y-%m-%d").date()

        def calc_priority(subject: SubjectInput) -> int:
            base = subject.priority or 5
            if getattr(subject, "is_retake", False):
                base += 2
            return min(10, base)

        entries = []
        for index, subject in enumerate(input.subjects):
            try:
                start_date = parse_date(subject.start_date)
                end_date = parse_date(subject.end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Định dạng ngày không hợp lệ cho môn {subject.name}.")
            entries.append({
                "data": subject,
                "priority": calc_priority(subject),
                "start": start_date,
                "end": end_date,
                "original_index": index,
            })

        removed_conflicts = []
        alternative_sessions_used = []

        def find_conflicts(items):
            conflicts = []
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    a = items[i]
                    b = items[j]
                    # Kiểm tra trùng khoảng thời gian
                    if b["start"] <= a["start"] <= b["end"] or a["start"] <= b["start"] <= a["end"]:
                        # Kiểm tra trùng giờ học
                        a_start_time = a["data"].start_time
                        a_end_time = a["data"].end_time
                        b_start_time = b["data"].start_time
                        b_end_time = b["data"].end_time
                        if (a_start_time < b_end_time and a_end_time > b_start_time):
                            conflicts.append((a, b))
            return conflicts

        async def find_alternative_sessions_from_db(original_code: str, semester: str, 
                                                   conflicting_with: dict, 
                                                   all_active_entries: list,
                                                   remove_entry_ref: dict):
            """Tìm sessions thay thế từ database"""
            query = {"metadata.original_code": original_code}
            if semester:
                query["semester"] = semester
            
            courses = await Course.find(query).to_list()
            alternatives = []
            
            for course in courses:
                if not course.metadata or "start_date" not in course.metadata:
                    continue
                
                try:
                    alt_start_date = parse_date(course.metadata.get("start_date"))
                    alt_end_date = parse_date(course.metadata.get("end_date"))
                except:
                    continue
                
                # Tạo SubjectInput từ course
                class AltSubject:
                    def __init__(self, course_data, metadata):
                        self.name = course_data.name
                        self.code = course_data.code
                        self.start_time = metadata.get("start_time", "07:00")
                        self.end_time = metadata.get("end_time", "11:30")
                        self.start_date = metadata.get("start_date")
                        self.end_date = metadata.get("end_date")
                        self.credits = course_data.credits
                        self.instructor = course_data.department or ""
                        self.subject_type = "Lý thuyết"
                        self.is_retake = getattr(remove_entry_ref["data"], "is_retake", False)  # Giữ nguyên is_retake
                        self.priority = remove_entry_ref["data"].priority  # Giữ nguyên priority từ subject
                
                alt_subject = AltSubject(course, course.metadata)
                
                alt_entry = {
                    "data": alt_subject,
                    "priority": remove_entry_ref["priority"],  # Giữ nguyên priority
                    "start": alt_start_date,
                    "end": alt_end_date,
                    "original_index": remove_entry_ref["original_index"],  # Giữ nguyên index
                }
                
                # Kiểm tra không trùng với môn đang conflict (keep_entry)
                conflict_with_keep = False
                if (conflicting_with["start"] <= alt_start_date <= conflicting_with["end"] or 
                    alt_start_date <= conflicting_with["start"] <= alt_end_date):
                    # Kiểm tra trùng giờ học
                    keep_start_time = conflicting_with["data"].start_time
                    keep_end_time = conflicting_with["data"].end_time
                    alt_start_time = alt_subject.start_time
                    alt_end_time = alt_subject.end_time
                    if (alt_start_time < keep_end_time and alt_end_time > keep_start_time):
                        conflict_with_keep = True
                
                if conflict_with_keep:
                    continue
                
                # Kiểm tra không trùng với các môn khác trong active_entries
                has_conflict = False
                for active_entry in all_active_entries:
                    # Bỏ qua chính remove_entry (so sánh bằng code)
                    if active_entry["data"].code == remove_entry_ref["data"].code:
                        continue
                    if (active_entry["start"] <= alt_start_date <= active_entry["end"] or 
                        alt_start_date <= active_entry["start"] <= alt_end_date):
                        # Kiểm tra trùng giờ học
                        active_start_time = active_entry["data"].start_time
                        active_end_time = active_entry["data"].end_time
                        alt_start_time = alt_subject.start_time
                        alt_end_time = alt_subject.end_time
                        if (alt_start_time < active_end_time and alt_end_time > active_start_time):
                            has_conflict = True
                            break
                
                if not has_conflict:
                    alternatives.append(alt_entry)
            
            return alternatives

        active_entries = entries[:]
        max_iterations = len(entries) * 3
        iteration = 0
        
        # Lấy semester từ subjects (nếu có) hoặc mặc định
        semester_from_subjects = None
        if input.subjects and hasattr(input.subjects[0], 'code'):
            # Có thể lấy từ metadata hoặc để mặc định
            semester_from_subjects = "2024-2"  # Mặc định, có thể cải thiện sau
        
        while iteration < max_iterations:
            conflicts = find_conflicts(active_entries)
            if not conflicts:
                break
            
            entry_a, entry_b = conflicts[0]
            
            # Logic ưu tiên
            if entry_a["priority"] > entry_b["priority"]:
                keep_entry, remove_entry = entry_a, entry_b
            elif entry_b["priority"] > entry_a["priority"]:
                keep_entry, remove_entry = entry_b, entry_a
            else:
                is_retake_a = getattr(entry_a["data"], "is_retake", False)
                is_retake_b = getattr(entry_b["data"], "is_retake", False)
                if is_retake_a and not is_retake_b:
                    keep_entry, remove_entry = entry_a, entry_b
                elif is_retake_b and not is_retake_a:
                    keep_entry, remove_entry = entry_b, entry_a
                else:
                    if entry_a["original_index"] < entry_b["original_index"]:
                        keep_entry, remove_entry = entry_a, entry_b
                    elif entry_b["original_index"] < entry_a["original_index"]:
                        keep_entry, remove_entry = entry_b, entry_a
                    else:
                        if entry_a["start"] <= entry_b["start"]:
                            keep_entry, remove_entry = entry_a, entry_b
                        else:
                            keep_entry, remove_entry = entry_b, entry_a

            # TRƯỚC KHI LOẠI BỎ: Thử tìm alternative session từ database
            remove_code = getattr(remove_entry["data"], "code", "")
            original_code = None
            
            if "-G" in remove_code:
                original_code = remove_code.split("-G")[0]
            else:
                original_code = remove_code
            
            if original_code:
                # Tìm sessions thay thế từ database
                alternatives = await find_alternative_sessions_from_db(
                    original_code,
                    semester_from_subjects,
                    keep_entry,
                    active_entries,
                    remove_entry  # Truyền remove_entry vào hàm
                )
                
                if alternatives:
                    # Chọn session tốt nhất (ưu tiên available_slots nếu có)
                    best_alternative = None
                    available_slots = input.available_time_slots if input.available_time_slots else []
                    
                    # Lấy thông tin day từ course metadata trong alternatives
                    # Ưu tiên sessions trong available_slots
                    for alt in alternatives:
                        # Lấy day từ course metadata (đã có trong alt_entry)
                        # Cần query lại course để lấy day chính xác
                        alt_course = await Course.find_one({"code": alt["data"].code})
                        if alt_course and alt_course.metadata:
                            alt_day = alt_course.metadata.get("day", "T2")
                        else:
                            alt_day = "T2"  # Mặc định
                        
                        alt_time = alt["data"].start_time
                        # Map time to slot
                        if "07:00" <= alt_time <= "11:30":
                            slot_period = "Sáng"
                        elif "12:30" <= alt_time <= "17:00":
                            slot_period = "Chiều"
                        else:
                            slot_period = "Tối"
                        slot = f"{alt_day}_{slot_period}"
                        
                        if slot in available_slots:
                            best_alternative = alt
                            break
                    
                    if not best_alternative:
                        best_alternative = alternatives[0]
                    
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
                    iteration += 1
                    continue

            # Không tìm thấy alternative, loại bỏ môn học
            removed_conflicts.append({
                "subject": remove_entry["data"].name,
                "kept_with": keep_entry["data"].name,
                "reason": f"{remove_entry['data'].start_date} - {remove_entry['data'].end_date} trùng với {keep_entry['data'].name}",
            })
            active_entries = [entry for entry in active_entries if entry is not remove_entry]
            iteration += 1

        if not active_entries:
            detail_msg = ", ".join([drop["subject"] for drop in removed_conflicts]) or "không xác định"
            raise HTTPException(
                status_code=400,
                detail=f"Không thể tạo thời khóa biểu vì tất cả môn đều trùng thời gian ({detail_msg})."
            )

        # Tạo danh sách tất cả các slot có thể
        all_possible_slots = [
            'T2_Sáng', 'T2_Chiều', 'T2_Tối',
            'T3_Sáng', 'T3_Chiều', 'T3_Tối',
            'T4_Sáng', 'T4_Chiều', 'T4_Tối',
            'T5_Sáng', 'T5_Chiều', 'T5_Tối',
            'T6_Sáng', 'T6_Chiều', 'T6_Tối',
            'T7_Sáng', 'T7_Chiều', 'T7_Tối',
            'CN_Sáng', 'CN_Chiều', 'CN_Tối',
        ]
        
        available_slots = input.available_time_slots if input.available_time_slots else all_possible_slots
        unavailable_slots = [slot for slot in all_possible_slots if slot not in available_slots]
        time_slots_for_ga = available_slots + unavailable_slots
        
        subject_names = [entry["data"].name for entry in active_entries]
        priorities = {entry["data"].name: entry["priority"] for entry in active_entries}
        subject_details = {}
        for entry in active_entries:
            subject = entry["data"]
            subject_details[subject.name] = {
                "instructor": subject.instructor,
                "start_time": subject.start_time,
                "end_time": subject.end_time,
                "start_date": subject.start_date,
                "end_date": subject.end_date,
                "priority": entry["priority"],
                "is_retake": subject.is_retake or False,
                "preferred_days": getattr(subject, "preferred_days", None) or [],
            }
        
        additional_constraints_dict = {}
        if input.additionalConstraints:
            additional_constraints_dict = {
                'avoidConsecutive': input.additionalConstraints.avoidConsecutive,
                'balanceDays': input.additionalConstraints.balanceDays,
                'preferMorning': input.additionalConstraints.preferMorning,
                'allowSaturday': input.additionalConstraints.allowSaturday
            }
        
        additional_constraints_dict['available_slots'] = available_slots
        additional_constraints_dict['unavailable_slots'] = unavailable_slots
        
        # Chạy GA
        final_schedule, final_cost = find_optimal_schedule(
            subject_names,
            time_slots_for_ga,
            input.constraints,
            priorities,
            additional_constraints_dict,
            subject_details
        )
        
        formatted_schedule = []
        for item in final_schedule:
            subject_name = item['subject']
            slot_name = item['time']
            info = subject_details[subject_name]
            formatted_schedule.append({
                "subject": subject_name,
                "time": slot_name,
                "instructor": info["instructor"],
                "sessions": 1,
                "start_date": info["start_date"],
                "end_date": info["end_date"],
                "start_time": info["start_time"],
                "end_time": info["end_time"],
                "priority": info["priority"],
                "is_retake": info["is_retake"],
            })
        
        new_schedule = Schedule(
            user_id=current_user.id,
            schedule_data=formatted_schedule,
            cost=final_cost
        )
        
        await new_schedule.save()
        
        print(f"Đã lưu lịch mới vào DB, ID: {new_schedule.id}")
        
        return {
            "schedule": formatted_schedule,
            "cost": final_cost,
            "db_id": new_schedule.id,
            "removed_conflicts": removed_conflicts,
            "alternative_sessions": alternative_sessions_used,
        }
    
    except Exception as e:
        print(f"Lỗi GA: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý GA: {e}")

# =================
# CHẠY SERVER
# =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
