#!/usr/bin/env python3
"""
生成测试数据
用于开发和演示环境的数据填充
"""

import os
import sys
import random
import hashlib
from datetime import date, timedelta
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("错误：需要安装 psycopg2")
    print("运行：pip install psycopg2-binary")
    sys.exit(1)


def get_db_config():
    """从环境变量获取数据库配置"""
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "database": os.getenv("PGDATABASE", "breast_ai"),
        "user": os.getenv("PGUSER", "breast_ai_user"),
        "password": os.getenv("PGPASSWORD", "breast_ai_password"),
    }


# 测试数据池
FAMILY_NAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴", "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗"]
GIVEN_NAMES = ["芳", "秀英", "伟", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "涛", "明", "婷", "娜", "超", "兵", "平"]

CONSTITUTIONS = ["气郁质", "痰湿质", "血瘀质", "平和质", "气虚质", "阳虚质", "阴虚质", "湿热质", "特禀质"]

ZHENG_TYPES = {
    "气郁质": ["肝郁气滞", "肝郁化火"],
    "痰湿质": ["脾虚痰湿", "痰瘀互结"],
    "血瘀质": ["气滞血瘀", "瘀毒内阻"],
    "平和质": ["冲任失调"],
    "气虚质": ["气血两虚", "正气亏虚"],
    "阳虚质": ["脾肾阳虚"],
    "阴虚质": ["肝肾阴虚"],
    "湿热质": ["湿热蕴结"],
    "特禀质": ["冲任失调"],
}

RISK_LEVELS = ["low", "medium", "high", "very_high"]
RISK_WEIGHTS = [0.3, 0.4, 0.2, 0.1]

VISIT_TYPES = ["初诊", "复诊", "术后复查", "化疗后复查", "常规随访"]

BIRADS_CATEGORIES = ["1", "2", "3", "4A", "4B", "4C", "5"]
BIRADS_WEIGHTS = [0.05, 0.25, 0.30, 0.20, 0.12, 0.05, 0.03]


def generate_patient_no(seq):
    return f"P{date.today().strftime('%Y%m%d')}{seq:06d}"


def generate_visit_no(seq):
    return f"V{date.today().strftime('%Y%m%d')}{seq:06d}"


def random_date(start_years_ago=5, end_years_ago=0):
    """生成随机日期"""
    start = date.today() - timedelta(days=start_years_ago*365)
    end = date.today() - timedelta(days=end_years_ago*365)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_test_data(conn, patient_count=50):
    """生成测试数据"""
    cur = conn.cursor()
    
    print(f"生成 {patient_count} 个测试患者...")
    
    patient_ids = []
    for i in range(patient_count):
        # 基本信息
        name = random.choice(FAMILY_NAMES) + random.choice(GIVEN_NAMES)
        gender = "F"  # 乳腺癌患者绝大多数为女性
        birth_date = random_date(70, 30)  # 年龄 30-70 岁
        phone = f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"
        
        # 中医信息
        constitution = random.choice(CONSTITUTIONS)
        zheng_type = random.choice(ZHENG_TYPES[constitution])
        risk_level = random.choices(RISK_LEVELS, weights=RISK_WEIGHTS)[0]
        risk_score = round(random.uniform(0.3, 0.9), 2)
        
        patient_no = generate_patient_no(i + 1)
        
        try:
            cur.execute("""
                INSERT INTO patient (
                    patient_no, name, gender, birth_date, phone,
                    constitution, zheng_type, risk_level, risk_score,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                RETURNING id
            """, (patient_no, name, gender, birth_date, phone, 
                  constitution, zheng_type, risk_level, risk_score))
            
            patient_id = cur.fetchone()[0]
            patient_ids.append(patient_id)
            
        except psycopg2.IntegrityError:
            # 患者编号重复，跳过
            conn.rollback()
            continue
    
    conn.commit()
    print(f"✓ 成功插入 {len(patient_ids)} 个患者")
    
    # 生成随访记录
    print("生成随访记录...")
    visit_count = 0
    for patient_id in patient_ids:
        # 每个患者 1-3 次随访
        num_visits = random.randint(1, 3)
        
        for j in range(num_visits):
            visit_date = random_date(3, 0)
            visit_type = random.choice(VISIT_TYPES)
            visit_no = generate_visit_no(visit_count + 1)
            
            birads = random.choices(BIRADS_CATEGORIES, weights=BIRADS_WEIGHTS)[0]
            
            try:
                cur.execute("""
                    INSERT INTO visit (
                        patient_id, visit_no, visit_date, visit_type,
                        birads_category, created_by
                    ) VALUES (%s, %s, %s, %s, %s, 1)
                    RETURNING id
                """, (patient_id, visit_no, visit_date, visit_type, birads))
                
                visit_id = cur.fetchone()[0]
                visit_count += 1
                
            except psycopg2.IntegrityError:
                conn.rollback()
                continue
    
    conn.commit()
    print(f"✓ 成功插入 {visit_count} 条随访记录")
    
    # 统计
    cur.execute("SELECT COUNT(*) FROM patient")
    patient_total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM visit")
    visit_total = cur.fetchone()[0]
    
    cur.execute("""
        SELECT risk_level, COUNT(*) 
        FROM patient 
        GROUP BY risk_level 
        ORDER BY risk_level
    """)
    risk_stats = cur.fetchall()
    
    cur.execute("""
        SELECT birads_category, COUNT(*) 
        FROM visit 
        WHERE birads_category IS NOT NULL
        GROUP BY birads_category 
        ORDER BY birads_category
    """)
    birads_stats = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # 输出统计
    print("\n" + "="*50)
    print("测试数据生成完成!")
    print("="*50)
    print(f"总患者数：{patient_total}")
    print(f"总随访数：{visit_total}")
    print("\n风险等级分布:")
    for risk, count in risk_stats:
        print(f"  {risk}: {count}")
    
    print("\nBI-RADS 分布:")
    for birads, count in birads_stats:
        print(f"  {birads}: {count}")
    print("="*50)


def main():
    config = get_db_config()
    
    print(f"连接数据库：{config['database']}@{config['host']}")
    
    try:
        conn = psycopg2.connect(**config)
        print("✓ 数据库连接成功")
        
        # 生成测试数据
        generate_test_data(conn, patient_count=50)
        
    except psycopg2.Error as e:
        print(f"\n✗ 数据库错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
