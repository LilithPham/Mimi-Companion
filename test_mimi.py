import os
from ai_logic import MimiBrain

def main():
    print("🐾 CHÀO MỪNG ĐẾN VỚI TRẠM THỬ NGHIỆM MIMI 🐾")
    print("="*50)
    
    # 1. Nhập Key
    api_key = input("🔑 Nhập Google Gemini API Key của em vào đây: ")
    
    try:
        mimi = MimiBrain(api_key=api_key)
        print("\n✅ Đã đánh thức bộ não Mimi thành công!\n")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        return

    # 2. Test Luồng 1: Hỏi thăm theo chủ đề
    topic = input("📝 Em muốn Mimi hỏi về chủ đề gì? (vd: Family, Pets, Food): ")
    print("\n⏳ Mimi đang suy nghĩ câu hỏi...\n")
    
    question_data = mimi.generate_question(topic)
    
    print("--- 💬 MIMI HỎI ---")
    print(f"🙋‍♀️ Mimi: {question_data.mimi_greeting}")
    print(f"❓ Câu hỏi: {question_data.question_en}")
    print(f"🇻🇳 Dịch nghĩa: {question_data.full_translation_vi}")
    print(f"💡 Từ khóa gợi ý: {', '.join(question_data.hint_keywords)}")
    print("-------------------\n")

    # 3. Test Luồng 2: Trả lời và nhận Feedback
    print("🎙️ (Hãy giả vờ em là học viên đang nói sai ngữ pháp hoặc nói lạc đề)")
    user_answer = input("🗣️ Nhập câu trả lời của em: ")
    print("\n⏳ Mimi đang phân tích...\n")
    
    eval_data = mimi.evaluate_answer(question_data.question_en, user_answer)
    
    print("--- 💖 NHẬN XÉT CỦA MIMI ---")
    print(f"🎉 Khích lệ: {eval_data.overall_encouragement}\n")
    
    if eval_data.grammar_errors:
        print("🔍 Bắt lỗi Ngữ Pháp:")
        for err in eval_data.grammar_errors:
            print(f"   ❌ '{err.original}' -> ✅ '{err.correction}'\n   👉 Thầy/Cô Mimi giải thích: {err.explanation}")
    
    if eval_data.vocabulary_improvements:
        print("\n✨ Nâng cấp Từ Vựng:")
        for vocab in eval_data.vocabulary_improvements:
            print(f"   ❌ '{vocab.original}' -> ✅ '{vocab.correction}'\n   👉 Thầy/Cô Mimi giải thích: {vocab.explanation}")
            
    print(f"\n🧠 Logic Check (Có lạc đề không?): {eval_data.logic_check}")
    print(f"\n🌟 Thử nói như Tây nè: {eval_data.native_suggestion}")
    print("="*50)

if __name__ == "__main__":
    main()