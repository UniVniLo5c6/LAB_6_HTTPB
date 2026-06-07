#!/bin/bash

# Định nghĩa mã màu hiển thị cho đẹp và dễ nhìn
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}    [LAB 6] SCRIPT KIỂM TRA ĐỒNG NHẤT VÀ TOÀN VẸN DỮ LIỆU CDC    ${NC}"
echo -e "${BLUE}==================================================================${NC}"

# ==================================================================
# CHỨC NĂNG 1: Kiểm tra sự đồng nhất về số dòng ở mỗi bảng trên 2 CSDL
# ==================================================================
echo -e "\n${YELLOW}1. KIỂM TRA SỰ ĐỒNG NHẤT SỐ DÒNG (MYSQL VS POSTGRESQL)${NC}"
echo -e "------------------------------------------------------------------"
printf "%-15s | %-15s | %-15s | %-10s\n" "Tên Bảng" "Số dòng MySQL" "Số dòng Postgres" "Trạng thái"
echo -e "------------------------------------------------------------------"

tables=("users" "posts" "comments" "tags")

for tbl in "${tables[@]}"; do
    # Lấy số dòng từ MySQL
    mysql_count=$(docker exec -i mysql mysql -u debezium -pdbz sourcedb -N -e "SELECT COUNT(*) FROM $tbl;" 2>/dev/null | tr -d '[:space:]')

    # Lấy số dòng từ PostgreSQL
    pg_count=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM $tbl;" 2>/dev/null | tr -d '[:space:]')

    # So sánh kết quả
    if [ "$mysql_count" == "$pg_count" ] && [ ! -z "$mysql_count" ]; then
        status="${GREEN}KHỚP (OK)${NC}"
    else
        status="${RED}LỆCH (FAIL)${NC}"
    fi

    printf "%-15s | %-15s | %-15s | %b\n" "$tbl" "$mysql_count" "$pg_count" "$status"
done


# ==================================================================
# CHỨC NĂNG 2: Kiểm tra tính toàn vẹn của dữ liệu trên PostgreSQL
# ==================================================================
echo -e "\n${YELLOW}2. KIỂM TRA TÍNH TOÀN VẸN DỮ LIỆU TRÊN POSTGRESQL${NC}"
echo -e "------------------------------------------------------------------"

# Ý o.1: Tất cả user_id trong posts phải tồn tại trong users
echo -n "-> Kiểm tra khóa ngoại (posts.user_id -> users.id): "
fk_posts=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM posts WHERE user_id NOT IN (SELECT id FROM users);" 2>/dev/null | tr -d '[:space:]')
if [ "$fk_posts" == "0" ]; then
    echo -e "${GREEN}Hợp lệ (0 lỗi)${NC}"
else
    echo -e "${RED}Phát hiện $fk_posts dòng lỗi (user_id không tồn tại trong bảng users)${NC}"
fi

# Ý o.2: Tất cả post_id trong comments phải tồn tại trong posts
echo -n "-> Kiểm tra khóa ngoại (comments.post_id -> posts.id): "
fk_comments=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM comments WHERE post_id NOT IN (SELECT id FROM posts);" 2>/dev/null | tr -d '[:space:]')
if [ "$fk_comments" == "0" ]; then
    echo -e "${GREEN}Hợp lệ (0 lỗi)${NC}"
else
    echo -e "${RED}Phát hiện $fk_comments dòng lỗi (post_id không tồn tại trong bảng posts)${NC}"
fi

# Ý o.3: Không có giá trị NULL trong cột có cờ NOT NULL
echo -n "-> Kiểm tra cờ NOT NULL trên các cột bắt buộc: "
null_errors=0

# Quét kiểm tra null trên các cột có cờ NOT NULL của các bảng
null_users=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM users WHERE id IS NULL OR username IS NULL OR email IS NULL;" 2>/dev/null | tr -d '[:space:]')
null_posts=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM posts WHERE id IS NULL OR user_id IS NULL OR title IS NULL;" 2>/dev/null | tr -d '[:space:]')
null_comments=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM comments WHERE id IS NULL OR post_id IS NULL OR user_id IS NULL;" 2>/dev/null | tr -d '[:space:]')
null_tags=$(docker exec -i postgresql psql -U postgres -d targetdb -t -c "SELECT COUNT(*) FROM tags WHERE id IS NULL OR name IS NULL;" 2>/dev/null | tr -d '[:space:]')

total_null_errors=$((null_users + null_posts + null_comments + null_tags))

if [ "$total_null_errors" == "0" ]; then
    echo -e "${GREEN}Hợp lệ (0 dòng bị NULL)${NC}"
else
    echo -e "${RED}CẢNH BÁO: Phát hiện $total_null_errors cột bị vi phạm giá trị NULL!${NC}"
fi

echo -e "${BLUE}==================================================================${NC}"