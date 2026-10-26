# Library Management Website

## 1. Team Members

| **Name** | **Student ID** | **Responsibilities** |
|---|---|---|
| Dina Ibrahim Ebeid | 2304144 | Backend development, user authentication, book and author management, image upload functionality, and application integration. |
| Mohab Mohamed | 2304077 | Database design, frontend development, interface styling, testing, and project documentation. |

*Note: The responsibilities should reflect the actual contributions of each team member.*

## 2. Project Overview

This project is a web-based Library Management Website developed using Python, Flask, MySQL, HTML, and CSS.

The website allows users to manage books and authors through a simple and user-friendly interface. It also includes user registration and login functionality.

## 3. Features

- **User Registration:** Users can create an account.
- **User Login:** Registered users can log in to the website.
- **Book Management:** Add, view, edit, and delete books.
- **Author Management:** Add, view, edit, and delete authors.
- **Book Cover Upload:** Upload images for books.
- **Author Photo Upload:** Upload images for authors.
- **Database Integration:** Store and retrieve information using MySQL.
- **Responsive Styling:** Style the website's pages and forms using CSS.

## 4. Technologies Used

- Python
- Flask
- MySQL
- PyMySQL
- HTML
- CSS
- bcrypt
- python-dotenv
- Werkzeug

## 5. Project Structure

```text
LAB/
├── app.py
├── requirements.txt
├── .env
├── static/
│   ├── style.css
│   ├── background.jpg
│   └── uploads/
└── templates/
    ├── login.html
    ├── register.html
    ├── library.html
    ├── edit_book.html
    ├── edit_author.html
    └── todos.html
```

*Note: Update the structure to match the actual files and folders in your project.*

## 6. Requirements

Before running the project, make sure you have installed:

- Python 3
- MySQL Server
- pip (Python package installer)

## 7. Installation and Setup

### Step 1: Open the Project

Download or clone the project and open its folder in VS Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

On Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install the Required Packages

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Configure the required database settings in your `.env` file.

Example:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=registration
```

Replace `your_mysql_password` with your actual MySQL password.

**Security note:** Never publish your real `.env` file or database password to a public repository. Use a `.env.example` file containing placeholder values instead.

### Step 6: Set Up the Database

Start MySQL Server and ensure the database and required tables exist.

If database setup scripts are included in the project, execute them before running the application.

### Step 7: Run the Application

From the project directory, run:

```bash
python app.py
```

Open your browser and visit:

http://127.0.0.1:5000/

## 8. How to Use the Website

1. Open the website in your browser.
2. Register an account if required.
3. Log in using your credentials.
4. Navigate to the Library section.
5. Add books and authors.
6. Upload book covers and author photos.
7. Edit existing books and authors when needed.

## 9. Security Considerations

- Store database credentials in environment variables.
- Do not commit passwords or secret keys to version control.
- Validate uploaded files before saving them.
- Use secure password hashing for user authentication.

## 11. Conclusion

The Library Management Website demonstrates the integration of Python Flask and MySQL to build a web application. It provides practical experience with user authentication, database operations, file uploads, and frontend styling.
