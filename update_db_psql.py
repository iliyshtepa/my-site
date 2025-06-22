import psycopg2

conn = psycopg2.connect(
    host="dpg-d1c21tadbo4c73csgeaug-a",
    port="5432",
    dbname="dbname_r7g1",
    user="admin",
    password="NUcx6inEwt05RoIMaicMoKEB#tDW6}Hk"
)
cursor = conn.cursor()

# Добавим новое поле, если оно ещё не существует
try:
    cursor.execute("ALTER TABLE projects ADD COLUMN full_description TEXT")
except:
    print("Поле уже существует")

conn.commit()
conn.close()
print("Таблица 'projects' обновлена")

conn = psycopg2.connect(
    host="dpg-d1c21tadbo4c73csgeaug-a",
    port="5432",
    dbname="dbname_r7g1",
    user="admin",
    password="NUcx6inEwt05RoIMaicMoKEB#tDW6}Hk"
)
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
