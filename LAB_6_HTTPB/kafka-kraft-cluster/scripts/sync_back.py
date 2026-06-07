import mysql.connector
from datetime import datetime

# Kết nối đến MySQL
db = mysql.connector.connect(
    host="localhost",
    user="debezium",
    password="dbz",
    database="sourcedb",
    port=3306
)
cursor = db.cursor()
current_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print("⏳ Đang phục hồi dữ liệu sang MySQL để khớp với Postgres...")

# 1. Bù dữ liệu cho bảng users (Ghi đè hoặc chèn từ ID 999 đến 1002)
user_data = []
for i in range(999, 1003):
    user_data.append((i, f"user_{i}", f"user{i}@gmail.com", f"User {i}", "active", current_now, current_now))
cursor.executemany("INSERT IGNORE INTO users (id, username, email, full_name, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", user_data)

# 2. Bù dữ liệu cho 5000 posts (Gắn vào user_id = 1000)
post_data = []
for i in range(1, 5001):
    post_data.append((i, 1000, f"Title {i}", "Content...", "published", current_now, current_now))
cursor.executemany("INSERT IGNORE INTO posts (id, user_id, title, content, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", post_data)

# 3. Bù dữ liệu cho 10000 comments (Đã xóa bỏ hoàn toàn trường updated_at theo đúng cấu trúc MySQL)
print("👉 Đang bù 10000 Comments...")
for b in range(10):
    batch = []
    for i in range(1, 1001):
        comment_id = b * 1000 + i
        batch.append((comment_id, 1, 1000, "Comment...", current_now))
    cursor.executemany("INSERT IGNORE INTO comments (id, post_id, user_id, content, created_at) VALUES (%s, %s, %s, %s, %s)", batch)

db.commit()
print("🎉 Đã phục hồi dữ liệu thành công hoàn toàn trên MySQL!")
cursor.close()
db.close()