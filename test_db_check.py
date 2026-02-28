"""检查数据库表是否正确创建"""
import psycopg2

DB_URL = "postgresql://neondb_owner:npg_l18hVmetjJNX@ep-small-unit-a1kmmpo7-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# 查看现有表
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
tables = [row[0] for row in cur.fetchall()]
print(f"现有表: {tables}")

# 查看每个表的列
for table in tables:
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
    cols = cur.fetchall()
    print(f"\n📋 {table}:")
    for col_name, col_type in cols:
        print(f"   {col_name}: {col_type}")

cur.close()
conn.close()
