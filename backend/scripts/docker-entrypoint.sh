#!/bin/bash
# 等待 PostgreSQL 就绪并执行初始化

set -e

echo "等待 PostgreSQL 启动..."

# 等待数据库就绪
for i in {1..30}; do
    if pg_isready -h ${POSTGRES_HOST:-localhost} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-breast_ai}; then
        echo "PostgreSQL 已就绪"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 1
done

# 检查是否已初始化
RESULT=$(psql -h ${POSTGRES_HOST:-localhost} -U ${POSTGRES_USER:-breast_ai} -d ${POSTGRES_DB:-breast_ai} -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='patient';" 2>/dev/null || echo "0")

if [ "$RESULT" -gt 0 ]; then
    echo "数据库已初始化，跳过"
else
    echo "开始初始化数据库..."
    python scripts/init_db.py
fi

echo "数据库初始化完成"
