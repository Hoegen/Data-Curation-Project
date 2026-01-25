# First, close any existing connections
import mysql.connector

# Connect and kill processes
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234'
)
cursor = conn.cursor()

# See what's running
cursor.execute("SHOW PROCESSLIST")
processes = cursor.fetchall()
for process in processes:
    print(process)

# Kill your database connections (be careful!)
cursor.execute("SELECT CONCAT('KILL ', id, ';') FROM INFORMATION_SCHEMA.PROCESSLIST WHERE db = 'south_tyrol_hazards'")
kill_commands = cursor.fetchall()
for cmd in kill_commands:
    print(f"Would run: {cmd[0]}")
    cursor.execute(cmd[0])  # Uncomment to actually kill

conn.close()