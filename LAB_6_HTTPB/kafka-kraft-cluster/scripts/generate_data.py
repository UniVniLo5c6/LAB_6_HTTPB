import mysql.connector
from faker import Faker
import random
import time

fake = Faker()

# Ket noi den MySQL trong Docker
db = mysql.connector.connect(
    host="localhost",
    user="debezium",
    password="dbz",
    database="sourcedb",
    port=3306
)
cursor = db.cursor()

print("Dang tao du lieu mau...")

# Tao seed thoi gian de dam bao chuoi random khong bi trung khi chay nhieu lan
timestamp = int(time.time())

# 1. Tao 1000 users
print("Tao 1000 users...")
user_data = []
for i in range(1000):
    # Noi them timestamp va i vao sau username va email de dam bao tinh duy nhat neu chay nhieu lan
    unique_username = f"{fake.user_name()[:30]}_{timestamp}_{i}"
    unique_email = f"{i}_{timestamp}_{fake.email()[:60]}"
    full_name = fake.name()[:100]
    status = random.choice(['active', 'inactive', 'suspended'])

    user_data.append((unique_username, unique_email, full_name, status))

cursor.executemany("INSERT INTO users (username, email, full_name, status) VALUES (%s, %s, %s, %s)", user_data)
db.commit()

# --- FIX LOI: Lay danh sach user_id THUC TE tu database de random ---
cursor.execute("SELECT id FROM users")
valid_user_ids = [row[0] for row in cursor.fetchall()]
# --------------------------------------------------------------------

# 2. Tao 100 tags
print("Tao 100 tags...")
tag_data = [(f"tag_{timestamp}_{i}",) for i in range(100)]
cursor.executemany("INSERT IGNORE INTO tags (name) VALUES (%s)", tag_data)
db.commit()

# 3. Tao 5000 posts
print("Tao 5000 posts...")
post_data = []
for _ in range(5000):
    # Chon ngau nhien tu danh sach user_id CO THAT trong database
    user_id = random.choice(valid_user_ids)
    post_data.append((user_id, fake.sentence()[:200], fake.text(), random.choice(['draft', 'published', 'archived'])))
cursor.executemany("INSERT INTO posts (user_id, title, content, status) VALUES (%s, %s, %s, %s)", post_data)
db.commit()

# --- FIX LOI: Lay danh sach post_id THUC TE tu database de random cho bang comments ---
cursor.execute("SELECT id FROM posts")
valid_post_ids = [row[0] for row in cursor.fetchall()]
# --------------------------------------------------------------------------------------

# 4. Tao 10000 comments
print("Tao 10000 comments...")
# Chia nho batch de tranh loi bo nho
for i in range(10):
    batch = []
    for _ in range(1000):
        # Chon ngau nhien tu danh sach id CO THAT
        post_id = random.choice(valid_post_ids)
        user_id = random.choice(valid_user_ids)
        batch.append((post_id, user_id, fake.text()))
    cursor.executemany("INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)", batch)
    db.commit()

print("Hoan thanh tao du lieu mau!")
cursor.close()
db.close()