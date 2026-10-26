import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv(override=True)

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

app.secret_key = os.getenv("SESSION_SECRET")

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

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
            query = """
                SELECT todo_id, title, is_done, created_at
                FROM todos
                WHERE user_id = %s
                ORDER BY todo_id DESC;
            """
            cursor.execute(query, (session["user_id"],))
            todos = cursor.fetchall()
    finally:
        connection.close()

    open_count = sum(1 for todo in todos if not todo["is_done"])
    completed_count = sum(1 for todo in todos if todo["is_done"])

    return render_template(
        "todos.html",
        todos=todos,
        name=session["user_name"],
        open_count=open_count,
        completed_count=completed_count
    )

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


@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT author_id, name, country, photo FROM authors ORDER BY author_id"
            )
            authors = cursor.fetchall()

            cursor.execute(
                "SELECT book_id, title, price, author_id, cover FROM books ORDER BY book_id"
            )
            books = cursor.fetchall()

        return render_template(
            "library.html",
            authors=authors,
            books=books
        )
    finally:
        connection.close()



@app.route("/library/author/add", methods=["POST"])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("photo")
    photo_filename = None

    if not name or not country:
        flash("Please enter the author's name and country.")
        return redirect(url_for("library"))

    if image and image.filename:
        if not allowed_file(image.filename):
            flash("Please upload a valid image file.")
            return redirect(url_for("library"))

        photo_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO authors (name, country, photo) VALUES (%s, %s, %s)",
                (name, country, photo_filename)
            )
        connection.commit()
        flash("Author added successfully!")
    except Exception:
        connection.rollback()
        app.logger.exception("Could not add author")
        flash("Could not add author. Please check the application log.")
    finally:
        connection.close()

    return redirect(url_for("library"))



@app.route("/library/book/add", methods=["POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_id = request.form.get("author_id", "").strip()
    cover = request.files.get("cover")

    if not title or not price_text or not author_id:
        flash("Please complete all book fields.")
        return redirect(url_for("library"))

    try:
        price = float(price_text)
        author_id = int(author_id)


        cover_filename = None

        if cover and cover.filename:
                from werkzeug.utils import secure_filename
                cover_filename = secure_filename(cover.filename)
                upload_folder = os.path.join(app.static_folder, "uploads")
                os.makedirs(upload_folder, exist_ok=True)
                cover.save(os.path.join(upload_folder, cover_filename))


        if price < 0:
            raise ValueError("Price cannot be negative.")

        connection = get_db_connection()

        try:
            with connection.cursor() as cursor:
                              cursor.execute(
                    "INSERT INTO books (title, price, author_id, cover) "
                    "VALUES (%s, %s, %s, %s)",
                    (title, price, author_id, cover_filename)
                )
            connection.commit()
            flash("Book added successfully!")
        except Exception:
            connection.rollback()
            app.logger.exception("Could not add book")
            flash("Could not add book. Check the application log.")
        finally:
            connection.close()

    except (ValueError, TypeError):
        flash("Enter a valid price and author.")

    return redirect(url_for("library"))




@app.route("/library/author/edit/<int:author_id>", methods=["GET", "POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            if request.method == "POST":
                name = request.form.get("name", "").strip()
                country = request.form.get("country", "").strip()
                photo = request.files.get("photo")

                if not name or not country:
                    flash("Please enter the author's name and country.")
                    return redirect(
                        url_for("edit_author", author_id=author_id)
                    )

                cursor.execute(
                    "SELECT photo FROM authors WHERE author_id = %s",
                    (author_id,)
                )
                current_author = cursor.fetchone()

                if current_author is None:
                    flash("Author not found.")
                    return redirect(url_for("library"))

                photo_filename = current_author["photo"]

                if photo and photo.filename:
                    from werkzeug.utils import secure_filename
                    import uuid

                    photo_filename = (
                        str(uuid.uuid4()) + "_"
                        + secure_filename(photo.filename)
                    )

                    upload_folder = os.path.join(
                        app.static_folder, "uploads"
                    )
                    os.makedirs(upload_folder, exist_ok=True)

                    photo.save(
                        os.path.join(upload_folder, photo_filename)
                    )

                cursor.execute(
                    "UPDATE authors SET name = %s, country = %s, "
                    "photo = %s WHERE author_id = %s",
                    (name, country, photo_filename, author_id)
                )

                connection.commit()
                flash("Author updated successfully!")
                return redirect(url_for("library"))

            cursor.execute(
                "SELECT * FROM authors WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()

            if author is None:
                flash("Author not found.")
                return redirect(url_for("library"))

            return render_template("edit_author.html", author=author)

    except Exception:
        connection.rollback()
        app.logger.exception("Could not update author")
        flash("Could not update author. Check the application log.")
        return redirect(url_for("library"))

    finally:
        connection.close()





@app.route("/library/book/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            if request.method == "POST":
                title = request.form.get("title", "").strip()
                price_text = request.form.get("price", "").strip()
                author_text = request.form.get("author_id", "").strip()
                cover = request.files.get("cover")

                try:
                    price = float(price_text)
                    author_id = int(author_text)

                    if price < 0:
                        raise ValueError

                except (ValueError, TypeError):
                    flash("Enter a valid price and author.")
                    return redirect(url_for("edit_book", book_id=book_id))

                if not title:
                    flash("Please enter a book title.")
                    return redirect(url_for("edit_book", book_id=book_id))

                cursor.execute(
                    "SELECT cover FROM books WHERE book_id = %s",
                    (book_id,)
                )
                existing_book = cursor.fetchone()

                if existing_book is None:
                    flash("Book not found.")
                    return redirect(url_for("library"))

                cover_filename = existing_book["cover"]

                if cover and cover.filename:
                    from werkzeug.utils import secure_filename

                    cover_filename = secure_filename(cover.filename)
                    upload_folder = os.path.join(
                        app.static_folder, "uploads"
                    )
                    os.makedirs(upload_folder, exist_ok=True)
                    cover.save(os.path.join(upload_folder, cover_filename))

                cursor.execute(
                    """UPDATE books
                       SET title = %s, price = %s,
                           author_id = %s, cover = %s
                       WHERE book_id = %s""",
                    (title, price, author_id, cover_filename, book_id)
                )

                connection.commit()
                flash("Book updated successfully!")
                return redirect(url_for("library"))

            cursor.execute(
                """SELECT book_id, title, price, author_id, cover
                   FROM books WHERE book_id = %s""",
                (book_id,)
            )
            book = cursor.fetchone()

            if book is None:
                flash("Book not found.")
                return redirect(url_for("library"))

            cursor.execute(
                "SELECT author_id, name FROM authors ORDER BY name"
            )
            authors = cursor.fetchall()

            return render_template(
                "edit_book.html",
                book=book,
                authors=authors
            )

    except Exception:
        connection.rollback()
        app.logger.exception("Could not edit book")
        flash("Could not update book. Please check the application log.")
        return redirect(url_for("library"))

    finally:
        connection.close()



@app.route("/library/book/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM books WHERE book_id = %s",
                (book_id,)
            )
        connection.commit()
        flash("Book deleted successfully!")
    except Exception:
        connection.rollback()
        app.logger.exception("Could not delete book")
        flash("Could not delete book.")
    finally:
        connection.close()

    return redirect(url_for("library"))


@app.route("/delete_author/<int:author_id>", methods=["POST"])
def delete_author(author_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM authors WHERE author_id = %s",
                (author_id,)
            )
        connection.commit()
        flash("Author deleted successfully.", "success")
    finally:
        connection.close()

    return redirect(url_for("library"))


if __name__ == "__main__":
    app.run(debug=True)
