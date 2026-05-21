import json
import pandas as pd
import shutil
import os
import glob

# 1. Đọc file JSON chứa điểm của chuyên gia
json_path = 'speechocean762/scores.json'

with open(json_path, 'r', encoding='utf-8') as f:
    scores_data = json.load(f)

# 2. Chuyển đổi dữ liệu JSON thành Pandas DataFrame cho dễ thao tác
# Cấu trúc JSON của speechocean762 lấy key là ID của đoạn ghi âm
records = []
for audio_id, info in scores_data.items():
    records.append({
        'audio_id': audio_id,
        'accuracy_score': info.get('accuracy', 0) # Lấy điểm độ chính xác tổng thể
    })

df = pd.DataFrame(records)

# 3. Lọc ra 10 file tệ nhất (Hard cases) và 10 file tốt nhất (Good cases)
hard_cases = df.sort_values(by='accuracy_score', ascending=True).head(10)
good_cases = df.sort_values(by='accuracy_score', ascending=False).head(10)

# Gộp lại thành 1 list gồm 20 file cần thiết
test_dataset = pd.concat([hard_cases, good_cases])

# 4. Tạo thư mục output để gửi cho Vy
output_dir = 'mock_test_audio'
os.makedirs(output_dir, exist_ok=True)

# 5. Tìm và copy file âm thanh (do file wav nằm trong các thư mục con SPEAKER)
source_dir = 'speechocean762/WAVE'
found_count = 0

print("⏳ Đang trích xuất file âm thanh...")

for idx, row in test_dataset.iterrows():
    audio_id = row['audio_id']
    score = row['accuracy_score']
    
    # Tìm file có tên <audio_id>.wav trong mọi thư mục con của WAVE
    search_pattern = os.path.join(source_dir, '**', f"{audio_id}.wav")
    matched_files = glob.glob(search_pattern, recursive=True)
    
    if matched_files:
        src_path = matched_files[0]
        # Đổi tên file output để Vy nhìn vào biết ngay điểm gốc là bao nhiêu (VD: score_3.5_000123.wav)
        new_filename = f"score_{score}_{audio_id}.wav"
        dst_path = os.path.join(output_dir, new_filename)
        
        shutil.copy(src_path, dst_path)
        found_count += 1
        print(f"✅ Đã copy: {new_filename}")

print("-" * 30)
print(f"🎉 Hoàn tất! Đã lưu thành công {found_count}/20 file vào thư mục '{output_dir}'.")