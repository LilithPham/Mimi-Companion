import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models import MimiQuestion, MimiEvaluation

# --- BẮT ĐẦU ĐOẠN CODE ÉP ĐỌC FILE ---
# Lấy đường dẫn chính xác của thư mục dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Ép hệ thống đọc ĐÚNG cái file ở đường dẫn đó
load_dotenv(dotenv_path=ENV_PATH, override=True)

class MimiBrain:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Báo cáo thám tử (sẽ in ra ở màn hình đen Terminal)
        print(f"👉 Tọa độ két sắt: {ENV_PATH}")
        print(f"👉 Chìa khóa lấy được: {api_key}")
        
        if not api_key:
            raise ValueError(f"Không tìm thấy Key! Đã dò tìm tại: {ENV_PATH}")
            
        # ... (Phần code bên dưới của em giữ nguyên)
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", # Nên dùng bản 1.5 để tốc độ phản hồi nhanh nhất
            google_api_key=api_key,
            temperature=0.7 
        )
        # TẠO BỘ NHỚ: Nơi lưu trữ các câu hỏi và câu trả lời
        self.chat_history = ""

    def generate_question(self, topic: str) -> MimiQuestion:
        """Hàm tạo câu hỏi ĐẦU TIÊN khi chọn chủ đề"""
        self.chat_history = "" # Reset trí nhớ khi chọn chủ đề mới
        
        system_prompt = """
        Bạn là Mimi - một người bạn ảo cực kỳ dễ thương, chuyên giúp người Việt mất gốc (Level 0) luyện nói tiếng Anh.
        Hôm nay người dùng muốn nói chuyện về chủ đề: {topic}.
        
        NHIỆM VỤ:
        1. Đưa ra lời chào cổ vũ.
        2. Đặt 1 câu hỏi giao tiếp tiếng Anh đơn giản (A1-A2).
        3. Dịch trọn vẹn câu hỏi sang tiếng Việt.
        4. Gợi ý 3-5 từ vựng.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Bắt đầu thôi!")
        ])
        
        chain = prompt | self.llm.with_structured_output(MimiQuestion)
        result = chain.invoke({"topic": topic})
        
        # Lưu câu hỏi đầu tiên vào trí nhớ
        self.chat_history += f"\nMimi hỏi: {result.question_en}"
        return result

    def evaluate_answer(self, question: str, user_transcript: str) -> MimiEvaluation:
        """Hàm chấm điểm VÀ tạo câu hỏi TIẾP THEO"""
        
        # Cập nhật câu trả lời của User vào trí nhớ
        self.chat_history += f"\nNgười dùng trả lời: {user_transcript}"
        
        system_prompt = """
        Bạn là Mimi, người bạn đồng hành luyện nói tiếng Anh.
        
        NHIỆM VỤ 1 - CHẤM ĐIỂM:
        - Khen ngợi nỗ lực của họ.
        - Sửa lỗi ngữ pháp/từ vựng cơ bản bằng tiếng Việt dễ hiểu.
        - Kiểm tra xem họ có trả lời lạc đề không.
        - Gợi ý cách nói của người bản xứ.
        
        NHIỆM VỤ 2 - HỎI TIẾP (CỰC KỲ QUAN TRỌNG):
        - Bạn phải tạo ra một 'next_question' (câu hỏi tiếp theo).
        - Câu hỏi này PHẢI khai thác thông tin từ câu trả lời vừa rồi của người dùng.
        - Ví dụ: Nếu User nói "I have a dog", bạn hãy hỏi tiếp "What is your dog's name?" hoặc "What color is it?".
        - Không hỏi lại những câu đã hỏi trong Lịch sử trò chuyện.
        """
        
        human_prompt = f"""
        LỊCH SỬ TRÒ CHUYỆN NÃY GIỜ:
        {self.chat_history}
        
        Câu hỏi hiện tại của Mimi: {question}
        Câu trả lời vừa rồi của User: {user_transcript}
        
        Hãy chấm điểm và đặt câu hỏi tiếp theo!
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        chain = prompt | self.llm.with_structured_output(MimiEvaluation)
        result = chain.invoke({})
        
        # Cập nhật câu hỏi mới của Mimi vào trí nhớ để lần sau không hỏi trùng
        self.chat_history += f"\nMimi hỏi tiếp: {result.next_question.question_en}"
        
        return result
