#!/usr/bin/env python3
"""
数据库初始化脚本 - 简化版
使用 psycopg2 执行 SQL 文件
"""

import os
import sys
import time
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("错误：需要安装 psycopg2")
    print("运行：pip install psycopg2-binary")
    sys.exit(1)


def get_db_config():
    """从环境变量获取数据库配置"""
    return {
        "host": os.getenv("POSTGRES_HOST", os.getenv("PGHOST", "localhost")),
        "port": int(os.getenv("POSTGRES_PORT", os.getenv("PGPORT", "5432"))),
        "database": os.getenv("POSTGRES_DB", os.getenv("PGDATABASE", "breast_ai")),
        "user": os.getenv("POSTGRES_USER", os.getenv("PGUSER", "breast_ai_user")),
        "password": os.getenv("POSTGRES_PASSWORD", os.getenv("PGPASSWORD", "breast_ai_password")),
    }


def wait_for_db(config, max_retries=30):
    """等待数据库就绪"""
    print(f"等待 PostgreSQL 启动... ({config['host']}:{config['port']})")
    
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**config)
            conn.close()
            print("✓ PostgreSQL 已就绪")
            return True
        except psycopg2.OperationalError as e:
            print(f"  等待中... ({i+1}/{max_retries}) - {str(e)[:50]}")
            time.sleep(2)
    
    print("✗ PostgreSQL 启动超时")
    return False


def check_initialized(config):
    """检查数据库是否已初始化"""
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'patient'
        """)
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count > 0
    except Exception:
        return False


def init_database():
    """初始化数据库"""
    config = get_db_config()
    sql_file = Path(__file__).parent / "init_db.sql"
    
    if not sql_file.exists():
        print(f"✗ SQL 文件不存在：{sql_file}")
        sys.exit(1)
    
    # 等待数据库就绪
    if not wait_for_db(config):
        sys.exit(1)
    
    # 检查是否已初始化
    if check_initialized(config):
        print("✓ 数据库已初始化，跳过")
        return
    
    print(f"读取 SQL 文件：{sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    try:
        # 连接数据库
        print(f"连接到数据库 {config['database']}")
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # 执行 SQL
        print("执行数据库初始化...")
        cur.execute(sql_script)
        
        print("✓ 提交事务...")
        conn.commit()
        
        # 验证
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        cur.execute("""
            SELECT table_name FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        views = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT COUNT(*) FROM roles")
        roles_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM permissions")
        permissions_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM users")
        users_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        # 输出结果
        print("\n" + "="*50)
        print("数据库初始化完成!")
        print("="*50)
        print(f"✓ 创建表：{len(tables)} 张")
        for table in tables:
            print(f"    - {table}")
        
        if views:
            print(f"✓ 创建视图：{len(views)} 个")
            for view in views:
                print(f"    - {view}")
        
        print(f"\n✓ 初始数据:")
        print(f"    - 角色：{roles_count} 个")
        print(f"    - 权限：{permissions_count} 个")
        print(f"    - 用户：{users_count} 个")
        
        print("\n默认管理员账号:")
        print("    用户名：admin")
        print("    密码：admin123")
        print("="*50)
        
    except psycopg2.Error as e:
        print(f"\n✗ 数据库错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_database()
