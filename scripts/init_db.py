# init_db.py
import sqlite3
import os

def init_database():
    """创建示例数据库 sales.db"""
    db_path = "sales.db"
    
    # 如果数据库已存在，先删除（方便重新生成）
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ 已删除旧数据库")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建销售表
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            sale_date DATE NOT NULL,
            region TEXT NOT NULL
        )
    """)
    print("✅ 创建表 sales")
    
    # 插入示例数据
    sample_data = [
        ("笔记本电脑", "电子产品", 5999.00, "2026-07-01", "北京"),
        ("手机", "电子产品", 3299.00, "2026-07-03", "上海"),
        ("办公椅", "家具", 899.00, "2026-07-05", "北京"),
        ("咖啡机", "家电", 2599.00, "2026-07-10", "深圳"),
        ("显示器", "电子产品", 1499.00, "2026-07-12", "上海"),
        ("书桌", "家具", 1299.00, "2026-07-15", "北京"),
        ("吸尘器", "家电", 1899.00, "2026-07-18", "深圳"),
        ("平板电脑", "电子产品", 2699.00, "2026-07-20", "上海"),
        ("沙发", "家具", 3599.00, "2026-07-22", "北京"),
        ("空调", "家电", 4999.00, "2026-07-25", "深圳"),
        ("耳机", "电子产品", 499.00, "2026-08-01", "北京"),
        ("台灯", "家具", 299.00, "2026-08-02", "上海"),
        ("冰箱", "家电", 6999.00, "2026-08-03", "深圳"),
    ]
    
    cursor.executemany(
        "INSERT INTO sales (product, category, amount, sale_date, region) VALUES (?, ?, ?, ?, ?)",
        sample_data
    )
    
    conn.commit()
    conn.close()
    print(f"✅ 插入 {len(sample_data)} 条数据")
    print(f"✅ 数据库 {db_path} 创建成功！")

if __name__ == "__main__":
    init_database()