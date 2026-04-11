from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Cấu trúc cho một mục lỗi sai (Dùng cho cả Grammar và Vocab)
class FeedbackItem(BaseModel):
    original: str = Field(description="Từ hoặc cụm từ gốc người dùng nói sai")
    correction: str = Field(description="Cách sửa đúng hoặc hay hơn")
    explanation: str = Field(description="Giải thích lỗi sai bằng tiếng Việt thân thiện")

# 2. Hợp đồng cho câu hỏi của Mimi (Lúc đang chat)
class MimiQuestion(BaseModel):
    mimi_greeting: str = Field(description="Lời chào hoặc câu cổ vũ (vd: 'Chào Thu! Bạn sẵn sàng chưa?')")
    question_en: str = Field(description="Câu hỏi tiếng Anh Mimi đặt ra")
    full_translation_vi: str = Field(description="Bản dịch nghĩa toàn bộ câu hỏi sang tiếng Việt")
    hint_keywords: List[str] = Field(description="Danh sách các từ khóa gợi ý để người dùng trả lời")

# 3. Hợp đồng cho bảng đánh giá cuối cùng (Lúc bấm Stop)
class MimiEvaluation(BaseModel):
    user_transcript: str = Field(description="Toàn bộ văn bản người dùng đã nói")
    overall_encouragement: str = Field(description="Lời nhận xét tổng quát và động viên bằng tiếng Việt")
    
    grammar_errors: List[FeedbackItem] = Field(description="Danh sách lỗi ngữ pháp cơ bản")
    vocabulary_improvements: List[FeedbackItem] = Field(description="Danh sách gợi ý nâng cấp từ vựng")
    
    logic_check: str = Field(description="Nhận xét xem câu trả lời có đúng trọng tâm không")
    native_suggestion: str = Field(description="Phiên bản viết lại hoàn chỉnh nghe như người bản xứ")
    
    next_question: MimiQuestion = Field(description="Câu hỏi tiếp theo được tạo ra dựa trên câu trả lời của người dùng")
