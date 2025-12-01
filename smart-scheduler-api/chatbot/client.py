# smart-scheduler-api/chatbot/client.py

import aiohttp
import asyncio

# Ollama API Configuration
OLLAMA_API_URL = "http://localhost:11434/api/chat"

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
- Luôn ưu tiên đưa ra lời khuyên dựa trên ngành – viện – môn học – lịch thi – học kỳ – môn tiên quyết.
- Khi tư vấn, hãy hỏi lại thông tin còn thiếu (ngành, khóa, học kỳ, mong muốn của sinh viên).
- Đề xuất lịch học bằng cách giải thích lý do hợp lý.

Hãy luôn trả lời với vai trò là cố vấn học vụ hỗ trợ xếp lịch thông minh.
"""


async def get_bot_response(user_message: str, context_messages: list = None):
    """
    Lấy phản hồi từ Ollama (model gemma2:2b).
    
    Args:
        user_message: Tin nhắn của user
        context_messages: Danh sách tin nhắn trước đó để context (optional)
    
    Returns:
        str: Phản hồi từ Ollama AI
    """

    if context_messages is None:
        context_messages = []

    # Tạo danh sách messages với context
    messages = [{"role": "system", "content": PROMPT}]
    messages.extend(context_messages)
    messages.append({"role": "user", "content": user_message})

    # Payload cho Ollama API
    payload = {
        "model": "gemma2:2b",
        "messages": messages,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    OLLAMA_API_URL, 
                    json=payload, 
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return f"Lỗi server Ollama (status {resp.status}): {error_text[:200]}"

                    data = await resp.json()
                    if "message" in data and "content" in data["message"]:
                        return data["message"]["content"]
                    else:
                        return "Không nhận được phản hồi hợp lệ từ Ollama."
                        
            except asyncio.TimeoutError:
                raise Exception("Timeout: Ollama không phản hồi trong 60 giây. Vui lòng kiểm tra Ollama có đang chạy không.")
            except aiohttp.ClientConnectorError as e:
                raise Exception(f"Không thể kết nối đến Ollama tại {OLLAMA_API_URL}. Vui lòng kiểm tra Ollama đã được khởi động chưa (chạy 'ollama serve' trong terminal).")
            except aiohttp.ClientError as e:
                raise Exception(f"Lỗi kết nối đến Ollama: {str(e)}")

    except Exception as e:
        # Re-raise để main.py có thể xử lý
        raise

