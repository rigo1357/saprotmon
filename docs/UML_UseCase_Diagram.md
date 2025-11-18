# UML Use Case Diagram - Smart Scheduler System

## Tổng quan dự án
Hệ thống Smart Scheduler là một ứng dụng web thông minh sử dụng Giải thuật Di truyền (Genetic Algorithm) và AI để tự động tạo thời khóa biểu tối ưu cho sinh viên, giúp tránh trùng lịch và tối ưu hóa lịch học.

## Actors (Người dùng)

1. **Sinh viên (Student)**
2. **Quản trị viên (Admin)**
3. **Hệ thống (System)**

## Use Cases

### 1. Quản lý Tài khoản
- **UC-001: Đăng ký tài khoản** (Student)
- **UC-002: Đăng nhập** (Student, Admin)
- **UC-003: Đăng xuất** (Student, Admin)

### 2. Quản lý Môn học (Admin)
- **UC-004: Upload danh sách môn học** (Admin)
  - Upload file PDF/Excel/CSV
  - Tự động parse và lưu vào database
- **UC-005: Thêm môn học thủ công** (Admin)
- **UC-006: Xem danh sách môn học** (Admin)
- **UC-007: Lọc môn học theo học kỳ/chuyên ngành** (Admin)

### 3. Xếp Lịch Học (Student)
- **UC-008: Chọn môn học** (Student)
  - Xem danh sách môn học
  - Lọc theo học kỳ, chuyên ngành
  - Chọn môn học hiện tại
  - Chọn môn học lại
  - Tự động lấy tất cả sessions (nhóm/lớp) của môn học
  
- **UC-009: Thiết lập thời gian rảnh** (Student)
  - Chọn các ngày trong tuần (T2-CN)
  - Chọn các buổi học (Sáng, Chiều, Tối)
  
- **UC-010: Thiết lập ràng buộc** (Student)
  - Tránh xếp các môn học liên tiếp
  - Cân bằng số môn học giữa các ngày
  - Ưu tiên học buổi sáng
  - Cho phép học thứ 7
  
- **UC-011: Tạo thời khóa biểu** (Student)
  - Sử dụng Genetic Algorithm
  - Tự động xử lý trùng lịch
  - Tự động tìm sessions thay thế khi bị trùng
  - Ưu tiên môn học lại
  - Ưu tiên môn học được chọn đầu tiên
  
- **UC-012: Xem thời khóa biểu** (Student)
  - Hiển thị dạng bảng
  - Hiển thị thông tin chi tiết môn học
  
- **UC-013: Xuất thời khóa biểu** (Student)
  - Xuất file PDF
  - Xuất file Excel

### 4. Xử lý Trùng Lịch (System)
- **UC-014: Phát hiện trùng lịch** (System)
  - Kiểm tra trùng ngày học
  - Kiểm tra trùng giờ học
  
- **UC-015: Tự động tìm sessions thay thế** (System)
  - Tìm các sessions khác của cùng môn học (cùng original_code)
  - Kiểm tra sessions không trùng với môn khác
  - Tự động thay thế session bị trùng
  
- **UC-016: Ưu tiên môn học** (System)
  - Ưu tiên theo priority (1-10)
  - Ưu tiên môn học lại (is_retake)
  - Ưu tiên môn học được chọn đầu tiên
  - Ưu tiên môn học bắt đầu sớm hơn

### 5. Chatbot AI (Student)
- **UC-017: Chat với AI** (Student)
  - Hỏi về môn học
  - Hỏi về xếp lịch
  - Tư vấn học tập
  
- **UC-018: Xem lịch sử chat** (Student)
  - Xem các cuộc trò chuyện trước
  - Tìm kiếm trong lịch sử chat
  
- **UC-019: Xóa lịch sử chat** (Student)
  - Xóa một cuộc trò chuyện
  - Xóa tất cả lịch sử

## Use Case Diagram (Text Format)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART SCHEDULER SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Student    │
└──────┬───────┘
       │
       ├─── UC-001: Đăng ký tài khoản
       ├─── UC-002: Đăng nhập
       ├─── UC-003: Đăng xuất
       ├─── UC-008: Chọn môn học
       ├─── UC-009: Thiết lập thời gian rảnh
       ├─── UC-010: Thiết lập ràng buộc
       ├─── UC-011: Tạo thời khóa biểu
       │    └─── includes ───> UC-014: Phát hiện trùng lịch
       │    └─── includes ───> UC-015: Tự động tìm sessions thay thế
       │    └─── includes ───> UC-016: Ưu tiên môn học
       ├─── UC-012: Xem thời khóa biểu
       ├─── UC-013: Xuất thời khóa biểu
       ├─── UC-017: Chat với AI
       ├─── UC-018: Xem lịch sử chat
       └─── UC-019: Xóa lịch sử chat

┌──────────────┐
│    Admin     │
└──────┬───────┘
       │
       ├─── UC-002: Đăng nhập
       ├─── UC-003: Đăng xuất
       ├─── UC-004: Upload danh sách môn học
       ├─── UC-005: Thêm môn học thủ công
       ├─── UC-006: Xem danh sách môn học
       └─── UC-007: Lọc môn học

┌──────────────┐
│   System     │
└──────┬───────┘
       │
       ├─── UC-014: Phát hiện trùng lịch
       ├─── UC-015: Tự động tìm sessions thay thế
       └─── UC-016: Ưu tiên môn học
```

## Mô tả chi tiết Use Cases

### UC-011: Tạo thời khóa biểu
**Actor:** Student  
**Precondition:** Đã đăng nhập, đã chọn ít nhất 1 môn học  
**Main Flow:**
1. Student chọn các môn học
2. Student thiết lập thời gian rảnh
3. Student thiết lập ràng buộc
4. Student nhấn "Tạo thời khóa biểu"
5. System tự động lấy tất cả sessions của các môn học đã chọn
6. System phát hiện trùng lịch (UC-014)
7. System tự động tìm sessions thay thế (UC-015)
8. System áp dụng ưu tiên môn học (UC-016)
9. System chạy Genetic Algorithm để tối ưu
10. System trả về thời khóa biểu tối ưu
11. System hiển thị kết quả và thông báo các môn đã được tự động thay thế

**Alternative Flow:**
- 7a. Không tìm thấy session thay thế → Loại bỏ môn học và thông báo

### UC-015: Tự động tìm sessions thay thế
**Actor:** System  
**Precondition:** Đã phát hiện trùng lịch  
**Main Flow:**
1. System xác định môn học bị trùng (remove_entry)
2. System lấy original_code của môn học
3. System tìm tất cả courses có cùng original_code trong database
4. System lọc các sessions không trùng với môn học khác
5. System chọn session phù hợp nhất
6. System thay thế session bị trùng bằng session mới
7. System lưu thông tin về session đã được thay thế

**Alternative Flow:**
- 4a. Không tìm thấy session không trùng → Loại bỏ môn học

## Relationships

- **Include:** UC-011 includes UC-014, UC-015, UC-016
- **Extend:** UC-015 extends UC-014 (khi phát hiện trùng lịch)
- **Generalization:** UC-004 và UC-005 đều là "Quản lý môn học"

## Technology Stack

- **Backend:** FastAPI, Python, MongoDB, Beanie ODM
- **Frontend:** React.js, Framer Motion
- **AI:** Ollama, Gemma2 model
- **Algorithm:** Genetic Algorithm (custom implementation)
- **Export:** PDF, Excel

## Phân tích chi tiết Use Cases

### Bảng phân tích Use Cases

| STT | Tên Use Case | Ý nghĩa | Chức năng |
|-----|--------------|---------|-----------|
| **UC-001** | Đăng ký tài khoản | Cho phép sinh viên tạo tài khoản mới để sử dụng hệ thống, đảm bảo tính bảo mật và quản lý người dùng hiệu quả. | - Nhập thông tin: username, email, password<br>- Kiểm tra username đã tồn tại<br>- Hash mật khẩu bằng bcrypt<br>- Lưu thông tin vào database<br>- Trả về thông báo đăng ký thành công |
| **UC-002** | Đăng nhập | Xác thực danh tính người dùng, cấp quyền truy cập vào hệ thống và bảo vệ dữ liệu cá nhân. | - Nhập username và password<br>- Kiểm tra thông tin đăng nhập<br>- Tạo JWT token<br>- Lưu token vào localStorage (frontend)<br>- Chuyển hướng đến trang chính |
| **UC-003** | Đăng xuất | Đảm bảo an toàn khi người dùng kết thúc phiên làm việc, xóa thông tin xác thực và ngăn truy cập trái phép. | - Xóa JWT token khỏi localStorage<br>- Xóa thông tin user khỏi context<br>- Chuyển hướng về trang đăng nhập<br>- Hủy các session đang hoạt động |
| **UC-004** | Upload danh sách môn học | Giúp quản trị viên nhập hàng loạt môn học vào hệ thống một cách nhanh chóng, tiết kiệm thời gian và giảm sai sót. | - Chọn file (PDF/Excel/CSV)<br>- Upload file lên server<br>- Parse dữ liệu từ file<br>- Validate thông tin môn học<br>- Lưu vào database<br>- Hiển thị số lượng môn đã thêm và mẫu dữ liệu |
| **UC-005** | Thêm môn học thủ công | Cho phép quản trị viên thêm từng môn học với thông tin chi tiết, phù hợp khi cần bổ sung hoặc chỉnh sửa môn học đơn lẻ. | - Nhập thông tin: mã môn, tên môn, số tín chỉ, học kỳ, chuyên ngành, bộ môn<br>- Kiểm tra môn học đã tồn tại<br>- Lưu vào database<br>- Trả về thông tin môn học vừa tạo |
| **UC-006** | Xem danh sách môn học | Cung cấp cái nhìn tổng quan về tất cả môn học trong hệ thống, giúp quản trị viên quản lý và kiểm tra dữ liệu. | - Lấy danh sách môn học từ database<br>- Hiển thị dạng bảng hoặc danh sách<br>- Hiển thị: mã môn, tên môn, số tín chỉ, học kỳ, chuyên ngành<br>- Phân trang nếu có nhiều môn học |
| **UC-007** | Lọc môn học theo học kỳ/chuyên ngành | Giúp quản trị viên và sinh viên tìm kiếm môn học nhanh chóng theo tiêu chí cụ thể, tăng hiệu quả sử dụng hệ thống. | - Chọn học kỳ từ dropdown<br>- Chọn chuyên ngành từ dropdown<br>- Gửi request với filter parameters<br>- Nhận danh sách môn học đã lọc<br>- Hiển thị kết quả |
| **UC-008** | Chọn môn học | Cho phép sinh viên chọn các môn học muốn đăng ký, tự động lấy tất cả sessions (nhóm/lớp) để có nhiều lựa chọn thời gian học. | - Xem danh sách môn học (đã lọc theo học kỳ/chuyên ngành)<br>- Tìm kiếm môn học theo tên/mã<br>- Chọn môn học hiện tại hoặc môn học lại<br>- Tự động gọi API lấy tất cả sessions của môn học<br>- Thêm tất cả sessions vào danh sách đã chọn<br>- Xóa môn học khỏi danh sách đã chọn |
| **UC-009** | Thiết lập thời gian rảnh | Giúp sinh viên chỉ định các khung giờ có thể học, hệ thống sẽ ưu tiên xếp môn học vào những thời gian này để tối ưu lịch học. | - Chọn các ngày trong tuần (T2, T3, T4, T5, T6, T7, CN)<br>- Chọn các buổi học (Sáng, Chiều, Tối) cho mỗi ngày<br>- Lưu thông tin vào state<br>- Hiển thị trực quan bằng checkbox hoặc toggle |
| **UC-010** | Thiết lập ràng buộc | Cho phép sinh viên tùy chỉnh các yêu cầu bổ sung cho lịch học, giúp tạo ra thời khóa biểu phù hợp với nhu cầu cá nhân. | - Bật/tắt "Tránh xếp các môn học liên tiếp"<br>- Bật/tắt "Cân bằng số môn học giữa các ngày"<br>- Bật/tắt "Ưu tiên học buổi sáng"<br>- Bật/tắt "Cho phép học thứ 7"<br>- Lưu các ràng buộc vào state |
| **UC-011** | Tạo thời khóa biểu | Sử dụng Genetic Algorithm để tự động tạo lịch học tối ưu, tự động xử lý trùng lịch và tìm sessions thay thế, giúp sinh viên có lịch học hợp lý nhất. | - Thu thập thông tin: môn học đã chọn, thời gian rảnh, ràng buộc<br>- Chuẩn hóa dữ liệu môn học<br>- Phát hiện trùng lịch (UC-014)<br>- Tự động tìm sessions thay thế (UC-015)<br>- Áp dụng ưu tiên môn học (UC-016)<br>- Chạy Genetic Algorithm để tối ưu<br>- Tạo và lưu lịch học vào database<br>- Trả về kết quả và thông báo các môn đã được thay thế |
| **UC-012** | Xem thời khóa biểu | Hiển thị lịch học đã tạo dưới dạng trực quan, giúp sinh viên dễ dàng theo dõi và quản lý lịch học hàng tuần. | - Lấy dữ liệu lịch học từ database hoặc response<br>- Hiển thị dạng bảng với các cột: Buổi, Thứ 2-7, Chủ nhật<br>- Hiển thị thông tin môn học: tên môn, giảng viên, thời gian<br>- Highlight các ô có môn học<br>- Hiển thị khung giờ tương ứng |
| **UC-013** | Xuất thời khóa biểu | Cho phép sinh viên lưu trữ và chia sẻ lịch học dưới dạng file PDF hoặc Excel, tiện lợi cho việc in ấn và quản lý offline. | - Chọn định dạng xuất (PDF hoặc Excel)<br>- Tạo file từ dữ liệu lịch học<br>- Định dạng file với header, footer, styling<br>- Tải file về máy<br>- Hiển thị thông báo tải thành công |
| **UC-014** | Phát hiện trùng lịch | Tự động kiểm tra và phát hiện các môn học bị trùng thời gian, đảm bảo sinh viên không bị xung đột lịch học. | - So sánh khoảng thời gian học của các môn (start_date, end_date)<br>- Kiểm tra trùng ngày học<br>- So sánh giờ học (start_time, end_time)<br>- Kiểm tra trùng giờ học<br>- Trả về danh sách các cặp môn bị trùng |
| **UC-015** | Tự động tìm sessions thay thế | Khi phát hiện trùng lịch, hệ thống tự động tìm các nhóm/lớp khác của cùng môn học để thay thế, giảm thiểu số môn bị loại bỏ. | - Xác định môn học bị trùng (remove_entry)<br>- Lấy original_code của môn học<br>- Query database tìm tất cả courses có cùng original_code<br>- Lọc các sessions không trùng với môn đang conflict<br>- Lọc các sessions không trùng với các môn khác<br>- Ưu tiên sessions trong available_slots<br>- Chọn session phù hợp nhất<br>- Thay thế session bị trùng<br>- Lưu thông tin về session đã được thay thế |
| **UC-016** | Ưu tiên môn học | Áp dụng các quy tắc ưu tiên để quyết định môn học nào được giữ lại khi bị trùng lịch, đảm bảo môn học quan trọng được ưu tiên. | - So sánh priority (1-10, 10 là cao nhất)<br>- Kiểm tra is_retake (môn học lại được ưu tiên)<br>- So sánh original_index (môn chọn đầu tiên được ưu tiên)<br>- So sánh start_date (môn bắt đầu sớm hơn được ưu tiên)<br>- Quyết định môn học nào được giữ lại |
| **UC-017** | Chat với AI | Cung cấp trợ lý AI thông minh để tư vấn về môn học, xếp lịch và giải đáp thắc mắc, giúp sinh viên có thông tin và lời khuyên hữu ích. | - Nhập câu hỏi vào ô chat<br>- Gửi tin nhắn đến API<br>- Lấy lịch sử chat trước đó để context<br>- Gọi Ollama API với model Gemma2<br>- Nhận phản hồi từ AI<br>- Hiển thị tin nhắn trong giao diện chat<br>- Lưu tin nhắn vào database |
| **UC-018** | Xem lịch sử chat | Cho phép sinh viên xem lại các cuộc trò chuyện trước đó với AI, giúp tra cứu thông tin đã hỏi và tiếp tục cuộc trò chuyện. | - Lấy danh sách các session chat từ database<br>- Nhóm tin nhắn theo session_id<br>- Hiển thị danh sách các cuộc trò chuyện<br>- Hiển thị tin nhắn đầu tiên và thời gian<br>- Click để xem chi tiết cuộc trò chuyện<br>- Tìm kiếm trong lịch sử chat |
| **UC-019** | Xóa lịch sử chat | Cho phép sinh viên xóa các cuộc trò chuyện không cần thiết, quản lý dữ liệu cá nhân và giải phóng không gian lưu trữ. | - Chọn cuộc trò chuyện cần xóa<br>- Xác nhận xóa<br>- Gọi API xóa session<br>- Xóa tất cả tin nhắn trong session khỏi database<br>- Cập nhật danh sách hiển thị<br>- Hiển thị thông báo xóa thành công |

### Tóm tắt theo nhóm chức năng

#### 1. Quản lý Tài khoản (UC-001 đến UC-003)
Nhóm này đảm bảo tính bảo mật và quản lý người dùng, cho phép sinh viên và quản trị viên đăng ký, đăng nhập và đăng xuất an toàn.

#### 2. Quản lý Môn học (UC-004 đến UC-007)
Nhóm này hỗ trợ quản trị viên quản lý dữ liệu môn học, từ upload hàng loạt đến thêm thủ công và tìm kiếm, đảm bảo hệ thống có đầy đủ thông tin môn học.

#### 3. Xếp Lịch Học (UC-008 đến UC-013)
Nhóm này là chức năng cốt lõi của hệ thống, giúp sinh viên chọn môn học, thiết lập ràng buộc và tạo lịch học tối ưu bằng Genetic Algorithm, sau đó xem và xuất lịch học.

#### 4. Xử lý Trùng Lịch (UC-014 đến UC-016)
Nhóm này tự động hóa việc xử lý trùng lịch, phát hiện xung đột, tìm sessions thay thế và áp dụng quy tắc ưu tiên để đảm bảo lịch học hợp lý.

#### 5. Chatbot AI (UC-017 đến UC-019)
Nhóm này cung cấp trợ lý AI thông minh để tư vấn và hỗ trợ sinh viên, với khả năng lưu trữ và quản lý lịch sử chat.

