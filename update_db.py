import sqlite3

conn = sqlite3.connect("projects.db")
cursor = conn.cursor()

# Добавим новое поле, если оно ещё не существует
try:
    cursor.execute("ALTER TABLE projects ADD COLUMN full_description TEXT")
except:
    print("Поле уже существует")

conn.commit()
conn.close()
print("Таблица 'projects' обновлена")

conn = sqlite3.connect("projects.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS project_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id)
)
""")

conn.commit()
conn.close()
print("Таблица 'project_images' создана")
