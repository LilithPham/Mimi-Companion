import json
import pandas as pd
import shutil
import os
import glob

# ĐÃ CHỐT ĐƯỜNG DẪN CHÍNH XÁC 100%
json_path = 'speechocean762/speechocean762/resource/scores.json'

print(f"📖 Đang đọc file điểm tại: {json_path}")

with open(json_path, 'r', encoding='utf-8') as f:
    scores_data = json.load(f)

# Chuyển đổi JSON sang Pandas DataFrame
records = []
for audio_id, info in scores_data.items():
    records.append({
        'audio_id': audio_id,
        'accuracy_score': info.get('accuracy', 0)
    })

df = pd.DataFrame(records)

# Lọc 10 file tệ nhất và 10 file tốt nhất
hard_cases = df.sort_values(by='accuracy_score', ascending=True).head(10)
good_cases = df.sort_values(by='accuracy_score', ascending=False).head(10)
test_dataset = pd.concat([hard_cases, good_cases])

# Tạo thư mục output
output_dir = 'mock_test_audio'
os.makedirs(output_dir, exist_ok=True)

# Tìm và copy file âm thanh (.wav)
source_dir = 'speechocean762/speechocean762/WAVE'
found_count = 0

print("⏳ Đang trích xuất file âm thanh...")

for idx, row in test_dataset.iterrows():
    audio_id = row['audio_id']
    score = row['accuracy_score']
    
    # Quét tìm file wav bên trong thư mục WAVE
    search_pattern = os.path.join(source_dir, '**', f"{audio_id}.wav")
    matched_files = glob.glob(search_pattern, recursive=True)
    
    if matched_files:
        src_path = matched_files[0]
        new_filename = f"score_{score}_{audio_id}.wav"
        dst_path = os.path.join(output_dir, new_filename)
        
        shutil.copy(src_path, dst_path)
        found_count += 1
        print(f"✅ Đã copy: {new_filename}")

print("-" * 30)
print(f"🎉 Hoàn tất! Đã lưu thành công {found_count}/20 file vào thư mục '{output_dir}'.")