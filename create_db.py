import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE bookings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
room TEXT,
date TEXT,
time TEXT
)
""")

conn.commit()
conn.close()

print("Database created")