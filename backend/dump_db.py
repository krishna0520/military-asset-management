import sqlite3

conn = sqlite3.connect("assets.db")
with open("database_dump.sql", "w") as f:
    for line in conn.iterdump():
        f.write(line + "\n")
conn.close()
print("Done: database_dump.sql created")