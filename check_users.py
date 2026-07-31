import sqlite3
import os

# Correct path to the database file
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spendly.db')
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT id, name, email FROM users ORDER BY id')
users = c.fetchall()
print('Total users:', len(users))
for u in users:
    print('  ', dict(u))
conn.close()