import sqlite3

# Создаём подключение к базе
conn = sqlite3.connect("projects.db")
cursor = conn.cursor()

# Создаём таблицу
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    image TEXT
)
""")

# Добавим несколько проектов
cursor.executemany("""
INSERT INTO projects (title, description, image) VALUES (?, ?, ?)
""", [
    ("Площадка у школы №7", "Современная спортивная зона с безопасным покрытием.", "project1.jpg"),
    ("Парковая зона «Центр»", "Озеленение, дорожки, малые архитектурные формы.", "project2.jpg"),
    ("Улица Гагарина", "Асфальтирование с разметкой и бордюрами.", "project3.jpg")
])

conn.commit()
conn.close()
print("База данных создана и заполнена.")
