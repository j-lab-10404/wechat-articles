"""重置数据库 - 删除所有旧表"""
import psycopg2

DB_URL = "postgresql://neondb_owner:npg_l18hVmetjJNX@ep-small-unit-a1kmmpo7-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

# 查看现有表
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
tables = [row[0] for row in cur.fetchall()]
print(f"现有表: {tables}")

# 删除所有表
if tables:
    cur.execute("DROP TABLE IF EXISTS " + ", ".join(tables) + " CASCADE")
    print("✅ 所有表已删除")
else:
    print("没有表需要删除")

cur.close()
conn.close()
print("完成。后端重启后会自动创建新表。")
