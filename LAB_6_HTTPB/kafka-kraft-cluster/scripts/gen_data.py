import mysql.connector
from faker import Faker
import random
import time
from datetime import datetime

fake = Faker()

# Kết nối đến MySQL trong Docker
db = mysql.connector.connect(
    host="localhost",
    user="debezium",
    password="dbz",
    database="sourcedb",
    port=3306
)
cursor = db.cursor()

print(" Đang khởi tạo dữ liệu mẫu chuẩn Lab 6...")

# Tạo seed thời gian để đảm bảo dữ liệu không bị trùng khi chạy lại
timestamp = int(time.time())
# Định dạng thời gian chuẩn ISO 8601 giúp ích cho CDC và Postgres Timestamp
current_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 1. Tạo 1005 users (Tạo dư ra một chút để chắc chắn vượt mốc tối thiểu 1000 dòng)
print(" Đang tạo 1005 Users...")
user_data = []
for i in range(1005):
    unique_username = f"{fake.user_name()[:20]}_{timestamp}_{i}"
    unique_email = f"{i}_{timestamp}_{fake.email()[:40]}"
    full_name = fake.name()[:100]
    status = random.choice(['active', 'inactive', 'suspended'])

    # Bổ sung dữ liệu ngày tháng chuẩn
    user_data.append((unique_username, unique_email, full_name, status, current_now, current_now))

cursor.executemany(
    "INSERT INTO users (username, email, full_name, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
    user_data
)
db.commit()

# Lấy danh sách ID thực tế của Users vừa tạo
cursor.execute("SELECT id FROM users")
valid_user_ids = [row[0] for row in cursor.fetchall()]

# 2. Tạo 100 tags
print(" Đang tạo 100 Tags...")
tag_data = [(f"tag_{timestamp}_{i}",) for i in range(100)]
cursor.executemany("INSERT IGNORE INTO tags (name) VALUES (%s)", tag_data)
db.commit()

# 3. Tạo 5000 posts
print(" Đang tạo 5000 Posts...")
post_data = []
for i in range(5000):
    user_id = random.choice(valid_user_ids)
    title = fake.sentence()[:150]
    content = fake.text()
    status = random.choice(['draft', 'published', 'archived'])

    post_data.append((user_id, title, content, status, current_now, current_now))

cursor.executemany(
    "INSERT INTO posts (user_id, title, content, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
    post_data
)
db.commit()

# Lấy danh sách ID thực tế của Posts vừa tạo
cursor.execute("SELECT id FROM posts")
valid_post_ids = [row[0] for row in cursor.fetchall()]

# 4. Tạo 10000 comments
print("Đang tạo 10000 Comments (Chia làm 10 đợt)...")
for i in range(10):
    batch = []
    for _ in range(1000):
        post_id = random.choice(valid_post_ids)
        user_id = random.choice(valid_user_ids)
        content = fake.text()[:500]

        batch.append((post_id, user_id, content, current_now, current_now))

    cursor.executemany(
        "INSERT INTO comments (post_id, user_id, content, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
        batch
    )
    db.commit()

print("🎉 HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH RẢI DỮ LIỆU MẪU MƯỢT MÀ!")
cursor.close()
db.close()