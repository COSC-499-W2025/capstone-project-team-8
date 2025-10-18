import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in your database:")
print("-" * 40)
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 40)
print("Checking auth_user table:")
print("=" * 40)

# Check if there are any users
cursor.execute("SELECT COUNT(*) FROM auth_user")
user_count = cursor.fetchone()[0]
print(f"Total users in database: {user_count}")

if user_count > 0:
    cursor.execute("SELECT id, username, email, is_staff, is_superuser FROM auth_user LIMIT 5")
    users = cursor.fetchall()
    print("\nUsers:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Staff: {user[3]}, Superuser: {user[4]}")

conn.close()
