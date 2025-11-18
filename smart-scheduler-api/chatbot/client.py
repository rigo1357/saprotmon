# smart-scheduler-api/chatbot/client.py
from openai import OpenAI

# 1. Khởi tạo Client (sử dụng 1 lần)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # (Key này không bắt buộc với Ollama)
)

PROMPT = """
Bạn là **Cố vấn học vụ thông minh** của sinh viên Trường Đại học Thủ Dầu Một (TDMU).

Nhiệm vụ chính của bạn:
- Tư vấn chọn môn học theo ngành, viện, học kỳ.
- Gợi ý lịch học tối ưu dựa trên thời gian rảnh, số tín chỉ, độ khó môn và các môn tiên quyết.
- Giải đáp thắc mắc về hệ thống Smart Scheduler.
- Hỗ trợ sinh viên tạo thời khóa biểu hợp lý, tránh trùng giờ, quá tải hoặc vi phạm điều kiện tốt nghiệp.

Yêu cầu phong cách:
- Giao tiếp bằng **tiếng Việt tự nhiên**, thân thiện, tinh tế.
- Giọng văn giống một cố vấn thực sự: rõ ràng, dễ hiểu, chuyên nghiệp nhưng gần gũi.
- Có thể dùng emoji nhẹ nếu phù hợp (📚, ✅, 💡).
- Không sử dụng tiếng Anh trừ khi sinh viên yêu cầu.

Bạn phải:
- Luôn ưu tiên đưa ra lời khuyên dựa trên **ngành – viện – môn học – lịch thi – học kỳ – môn tiên quyết**.
- Khi tư vấn, hãy hỏi lại thông tin còn thiếu (ngành, khóa, học kỳ, mong muốn của sinh viên).
- Đề xuất lịch học bằng cách giải thích lý do (ví dụ: môn cơ sở ngành nên học trước, tránh đăng ký nhiều môn nặng cùng lúc).

Ví dụ:
Sinh viên: Em muốn xếp lịch kỳ 2 ngành CNTT.
Cố vấn: Được rồi, để mình hỗ trợ nhé. Kỳ 2 của CNTT thường có các môn cơ sở như Lập trình hướng đối tượng, Kiến trúc máy tính, Toán rời rạc… Bạn muốn học bao nhiêu tín chỉ và khung giờ nào thì thuận tiện nhất? 📚

Sinh viên: Em bị trùng giờ.
Cố vấn: Không sao, mình sẽ tìm nhóm học phần khác cho bạn. Hãy gửi mình mã môn và nhóm bạn đã chọn để mình kiểm tra giúp nhé. 💡

Hãy luôn trả lời với vai trò là cố vấn học vụ hỗ trợ xếp lịch thông minh.
"""


async def get_bot_response(user_message: str, context_messages: list = None):
    """
    Lấy phản hồi từ Ollama với model gemma2:9b (hoặc gemma2:2b nếu không có).
    
    Args:
        user_message: Tin nhắn của user
        context_messages: Danh sách tin nhắn trước đó để context (optional)
    
    HƯỚNG DẪN SỬ DỤNG:
    1. Đảm bảo Ollama đã được cài đặt và đang chạy:
       - Chạy lệnh: ollama serve
    2. Pull model cần thiết:
       - ollama pull gemma2:9b (khuyến nghị, chất lượng tốt hơn)
       - hoặc: ollama pull gemma2:2b (nhẹ hơn, nhanh hơn)
    3. Nếu gặp lỗi connection, kiểm tra:
       - Ollama đang chạy trên port 11434
       - Firewall không chặn kết nối
    """
    if context_messages is None:
        context_messages = []
    
    try:
        # Tạo danh sách messages với context
        messages = [{"role": "system", "content": PROMPT}]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": user_message})
        
        # Thử dùng model gemma2:9b trước (chất lượng tốt hơn)
        # Nếu không có thì sẽ fallback về gemma2:2b
        model_name = "gemma2:9b"
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.8,  # Tăng temperature để phản hồi tự nhiên hơn
                timeout=60.0  # Timeout 60 giây cho model lớn hơn
            )
        except Exception as model_error:
            # Nếu model 9b không có, thử model 2b
            if "model" in str(model_error).lower() or "not found" in str(model_error).lower():
                print(f"Model {model_name} không tìm thấy, thử gemma2:2b...")
                model_name = "gemma2:2b"
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.8,
                    timeout=30.0
                )
            else:
                raise model_error
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Lỗi khi gọi Ollama: {e}")
        error_msg = str(e).lower()
        
        # Kiểm tra loại lỗi và trả về message phù hợp
        if "connection" in error_msg or "refused" in error_msg:
            return "Xin lỗi, tôi không thể kết nối với mô hình AI. Vui lòng kiểm tra Ollama đã được khởi động chưa (chạy 'ollama serve' trong terminal)."
        elif "timeout" in error_msg:
            return "Xin lỗi, yêu cầu đã hết thời gian chờ. Vui lòng thử lại."
        elif "model" in error_msg or "not found" in error_msg:
            return "Xin lỗi, mô hình AI chưa được tải. Vui lòng chạy 'ollama pull gemma2:9b' hoặc 'ollama pull gemma2:2b' trong terminal."
        else:
            return f"Xin lỗi, tôi đang gặp sự cố: {str(e)[:100]}. Vui lòng thử lại sau."