# UML Use Case Diagram - Smart Scheduler System

## Tổng quan

File này chứa tài liệu UML Use Case Diagram cho hệ thống Smart Scheduler.

## Files

1. **UML_UseCase_Diagram.md** - Mô tả chi tiết các Use Cases
2. **UML_UseCase.puml** - File PlantUML để vẽ diagram (có thể mở bằng PlantUML hoặc VS Code extension)

## Cách sử dụng

### Xem diagram bằng PlantUML

1. Cài đặt PlantUML extension trong VS Code
2. Mở file `UML_UseCase.puml`
3. Nhấn `Alt + D` để preview diagram

### Hoặc sử dụng PlantUML Online

1. Truy cập: http://www.plantuml.com/plantuml/uml/
2. Copy nội dung file `UML_UseCase.puml`
3. Paste vào editor
4. Xem kết quả

## Tóm tắt Use Cases

### Actors
- **Student**: Sinh viên sử dụng hệ thống
- **Admin**: Quản trị viên quản lý môn học
- **System**: Hệ thống tự động xử lý

### Use Cases chính

1. **Quản lý Tài khoản** (3 use cases)
2. **Quản lý Môn học** (4 use cases) - Admin only
3. **Xếp Lịch Học** (6 use cases) - Student
4. **Xử lý Trùng Lịch** (3 use cases) - System
5. **Chatbot AI** (3 use cases) - Student

### Use Case quan trọng nhất

**UC-011: Tạo thời khóa biểu**
- Sử dụng Genetic Algorithm
- Tự động xử lý trùng lịch
- Tự động tìm sessions thay thế
- Ưu tiên môn học

## Mối quan hệ

- **Include**: UC-011 includes UC-014, UC-015, UC-016
- **Extend**: UC-015 extends UC-014 (khi phát hiện trùng lịch)

