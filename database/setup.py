import os

# Define the folder structure and files
files = {
    "requirements.txt": """Flask==3.1.0
PyMySQL==1.1.1
bcrypt==4.2.1
python-dotenv==1.0.1
""",
    ".env": """DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=registration
SESSION_SECRET=super_secret_random_key_here
""",
    ".env.example": """DB_HOST=localhost
DB_USER=root
DB_PASSWORD=fake_password
DB_NAME=registration
SESSION_SECRET=fake_secret
""",
    ".gitignore": """.env
__pycache__/
.DS_Store
""",
    "database/schema.sql": """DROP DATABASE IF EXISTS registration;
CREATE DATABASE registration;
USE registration;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE (email)
);

CREATE TABLE todos (
    todo_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    is_done TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (todo_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""",
    "static/style.css": """body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; display: flex; justify-content: center; }
.card, .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 600px; box-sizing: border-box; }
header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }
input[type="text"], input[type="email"], input[type="password"] { width: 100%; padding: 10px; margin: 8px 0 15px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
button { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
button:hover { background: #0056b3; }
.error-list { color: red; font-size: 14px; margin-bottom: 15px; padding-left: 20px; }
.todo-item { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.todo-item input[type="text"] { margin: 0; flex-grow: 1; }
.btn-save { background: #28a745; }
.btn-delete { background: #dc3545; }
.btn-logout { background: #6c757d; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; }
.empty-state { color: #666; text-align: center; padding: 20px; }
@media (max-width: 360px) {
    body { padding: 5px; }
    .todo-item { flex-direction: column; align-items: stretch; }
}
""",
    "templates/register.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="card">
        <h2>Register</h2>
        {% with messages = get_flashed_messages(category_filter=["register_error"]) %}
            {% if messages %}
                <ul class="error-list">
                    {% for message in messages %}<li>{{ message }}</li>{% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
        <form method="POST">
            <label>Name</label>
            <input type="text" name="name" required>
            <label>Email</label>
            <input type="email" name="email" required>
            <label>Password</label>
            <input type="password" name="password" required>
            <label>Confirm Password</label>
            <input type="password" name="confirm_password" required>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="{{ url_for('login') }}">Log in</a></p>
    </div>
</body>
</html>
""",
    "templates/login.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="card">
        <h2>Login</h2>
        {% with messages = get_flashed_messages(category_filter=["login_error"]) %}
            {% if messages %}
                <ul class="error-list">
                    {% for message in messages %}<li>{{ message }}</li>{% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
        <form method="POST">
            <label>Email</label>
            <input type="email" name="email" required>
            <label>Password</label>
            <input type="password" name="password" required>
            <button type="submit">Log In</button>
        </form>
        <p>Don't have an account? <a href="{{ url_for('register') }}">Register</a></p>
    </div>
</body>
</html>
""",
    "templates/todos.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>To-Do List</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h2>To-Do</h2>
            <div class="user-info">
                <span>Hi, {{ name }}</span>
                <a href="{{ url_for('logout') }}" class="btn-logout">Log out</a>
            </div>
        </header>

        {% with messages = get_flashed_messages(category_filter=["todo_error"]) %}
            {% if messages %}
                <ul class="error-list">
                    {% for message in messages %}<li>{{ message }}</li>{% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <form action="{{ url_for('add_todo') }}" method="POST" class="add-form">
            <input type="text" name="title" placeholder="What needs to be done?" required maxlength="200">
            <button type="submit">Add</button>
        </form>

        <div class="todo-list">
            {% if not todos %}
                <p class="empty-state">Your to-do list is empty. Add a task above!</p>
            {% endif %}
            {% for todo in todos %}
            <form action="{{ url_for('update_todo', todo_id=todo.todo_id) }}" method="POST" class="todo-item">
                <input type="checkbox" name="is_done" {% if todo.is_done %}checked{% endif %} onchange="this.form.submit()">
                <input type="text" name="title" value="{{ todo.title }}" maxlength="200" required>
                <button type="submit" class="btn-save">Save</button>
                <button type="submit" formaction="{{ url_for('delete_todo', todo_id=todo.todo_id) }}" formmethod="POST" class="btn-delete" onclick="return confirm('Are you sure?')">Delete</button>
            </form>
            {% endfor %}
        </div>
    </div>
</body>
</html>
""",
    "app.py": """import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("todo_list"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "register_error")
            return render_template("register.html")
        if password != confirm_password:
            flash("Passwords do not match", "register_error")
            return render_template("register.html")

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s);"
                cursor.execute(query, (email, name, hashed_pw))
                connection.commit()
                session["user_id"] = cursor.lastrowid
                session["user_name"] = name
                return redirect(url_for("todo_list"))
        except pymysql.err.IntegrityError:
            flash("Email Already Exists", "register_error")
            return render_template("register.html")
        finally:
            connection.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required", "login_error")
            return render_template("login.html")

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT user_id, name, password_hash FROM users WHERE email = %s;"
                cursor.execute(query, (email,))
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                    session["user_id"] = user["user_id"]
                    session["user_name"] = user["name"]
                    return redirect(url_for("todo_list"))
                else:
                    flash("Invalid email or password", "login_error")
        finally:
            connection.close()
        return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/todos")
def todo_list():
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC;"
            cursor.execute(query, (session["user_id"],))
            todos = cursor.fetchall()
    finally:
        connection.close()
    return render_template("todos.html", todos=todos, name=session["user_name"])

@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "todo_error")
    elif len(title) > 200:
        flash("Title is too long (200 characters at most)", "todo_error")
    else:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO todos (user_id, title) VALUES (%s, %s);"
                cursor.execute(query, (session["user_id"], title))
                connection.commit()
        finally:
            connection.close()
    return redirect(url_for("todo_list"))

@app.route("/todos/update/<int:todo_id>", methods=["POST"])
def update_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    is_done = 1 if request.form.get("is_done") == "on" else 0
    if not title:
        flash("Title is required", "todo_error")
    elif len(title) > 200:
        flash("Title is too long (200 characters at most)", "todo_error")
    else:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE todos SET title = %s, is_done = %s WHERE todo_id = %s AND user_id = %s;"
                cursor.execute(query, (title, is_done, todo_id, session["user_id"]))
                connection.commit()
        finally:
            connection.close()
    return redirect(url_for("todo_list"))

@app.route("/todos/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM todos WHERE todo_id = %s AND user_id = %s;"
            cursor.execute(query, (todo_id, session["user_id"]))
            connection.commit()
    finally:
        connection.close()
    return redirect(url_for("todo_list"))

if __name__ == "__main__":
    app.run(debug=True)
"""
}

for filepath, content in files.items():
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Project folder structure and files created successfully!")