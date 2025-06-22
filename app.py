from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from functools import wraps
from flask_migrate import Migrate
from datetime import datetime


app = Flask(__name__)
app.secret_key = "spetsstroy_super_secret_2025"

# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:NUcx6inEwt05RoIMaioMoKEBftDW6jHk@dpg-d1c21tadbo4c73cgeaug-a.oregon-postgres.render.com:5432/dbname_r7c1'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Папка для загрузки изображений
UPLOAD_FOLDER = os.path.join("static", "img")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# База данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 🔐 Защита маршрутов
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Модели
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    image = db.Column(db.String(255))

class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    filename = db.Column(db.String(255))

class News(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(150), nullable=False)
    summary     = db.Column(db.Text,        nullable=False)   # краткое описание
    content     = db.Column(db.Text)                          # полный текст (опционально)
    image      = db.Column(db.String(255)) 
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Публичные маршруты
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        contact = ContactMessage(name=name, email=email, phone=phone, message=message)
        db.session.add(contact)
        db.session.commit()
        return render_template("contacts.html", success=True)
    return render_template("contacts.html", success=False)

@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    images = ProjectImage.query.filter_by(project_id=project_id).all()
    return render_template("project_detail.html", project=project, images=images)

@app.route("/news")
def news():
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template("news.html", news=news_items)

@app.route("/news/<int:news_id>")
def news_detail(news_id):
    item = News.query.get_or_404(news_id)
    return render_template("news_detail.html", item=item)

# Авторизация
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin"] = True
            return redirect("/admin")
        return render_template("login.html", error="Неверный логин или пароль")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# Админка
@app.route("/admin")
@admin_required
def admin_dashboard():
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    return render_template("admin/dashboard.html", unread_count=unread_count)

@app.route("/admin/projects")
@admin_required
def admin_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template("admin/projects.html", projects=projects)

@app.route("/admin/add-project", methods=["GET", "POST"])
@admin_required
def add_project():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        full_description = request.form.get("full_description")
        file = request.files.get("image")

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
        else:
            filename = "default.jpg"

        project = Project(title=title, description=description,
                          full_description=full_description, image=filename)
        db.session.add(project)
        db.session.commit()
        return redirect("/admin/projects")
    return render_template("admin/add_project.html")

@app.route("/admin/edit/<int:project_id>", methods=["GET", "POST"])
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        project.title = request.form.get("title")
        project.description = request.form.get("description")
        project.full_description = request.form.get("full_description")

        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            project.image = filename

        db.session.commit()
        return redirect("/admin/projects")

    return render_template("admin/edit_project.html", project=project)

# список новостей
@app.route("/admin/news")
@admin_required
def admin_news():
    items = News.query.order_by(News.id.desc()).all()
    return render_template("admin/news.html", items=items)

# добавление
@app.route("/admin/news/add", methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "POST":
        title   = request.form.get("title")
        summary = request.form.get("summary")
        content = request.form.get("content")
        file    = request.files.get("image")

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        news = News(title=title, summary=summary,
                    content=content, image=filename)
        db.session.add(news)
        db.session.commit()
        return redirect("/admin/news")
    return render_template("admin/add_news.html")

# редактирование
@app.route("/admin/news/edit/<int:news_id>", methods=["GET", "POST"])
@admin_required
def edit_news(news_id):
    item = News.query.get_or_404(news_id)
    if request.method == "POST":
        item.title   = request.form.get("title")
        item.summary = request.form.get("summary")
        item.content = request.form.get("content")

        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            item.image = filename

        db.session.commit()
        return redirect("/admin/news")
    return render_template("admin/edit_news.html", item=item)

# удаление
@app.route("/admin/news/delete/<int:news_id>", methods=["POST"])
@admin_required
def delete_news(news_id):
    item = News.query.get_or_404(news_id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/admin/news")



@app.route("/admin/messages")
@admin_required
def view_messages():
    messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
    return render_template("admin/messages.html", messages=messages)

@app.route("/admin/messages/read/<int:message_id>", methods=["POST"])
@admin_required
def mark_as_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return redirect("/admin/messages")


@app.route("/admin/messages/delete/<int:message_id>", methods=["POST"])
@admin_required
def delete_message(message_id):
    print(f"Удаляю сообщение с ID: {message_id}")
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect("/admin/messages")



@app.route("/delete-project/<int:project_id>", methods=["POST"])
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    ProjectImage.query.filter_by(project_id=project.id).delete()
    db.session.delete(project)
    db.session.commit()
    return redirect("/admin/projects")

@app.route("/admin/upload-images/<int:project_id>", methods=["GET", "POST"])
@admin_required
def upload_images(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        files = request.files.getlist("images")
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                db.session.add(ProjectImage(project_id=project.id, filename=filename))
        db.session.commit()
        return redirect("/admin/projects")

    return render_template("admin/upload_images.html", project_id=project_id)

# Запуск
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
