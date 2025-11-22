import sqlite3

conn = sqlite3.connect('lms.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in lms.db:", tables)

if 'users' in tables:
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Users table exists with {count} users")
else:
    print("Users table does NOT exist!")

conn.close()
