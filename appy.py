from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/partners")
def partners():
    return render_template("partners.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

# ← Блок запуска должен быть В КОНЦЕ
if __name__ == "__main__":
    app.run(debug=True)
