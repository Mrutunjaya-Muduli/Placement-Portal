# 🎓 Placement Management System

Welcome to the **Placement Portal**, a secure, robust web application built using **Django** and **Bootstrap 5**. This portal serves as a bridge between students and recruiting companies, simplifying the job listing, application, and candidate screening processes.

---

## 🚀 How to Run the Project

Follow these steps to activate the environment and start the development server on your local machine:

### 1. Open Terminal/PowerShell
Ensure you are in the project root directory:
```bash
cd d:\placement-manage
```

### 2. Activate the Virtual Environment
Activate the pre-configured Python virtual environment (`venv`):
- **On Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **On Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

### 3. Start the Django Server
Run the local development server:
```bash
python manage.py runserver
```

Once started, open your web browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🗄️ Database Connection & Configuration

The project is configured to use **SQLite** as its default database engine. This is ideal for development as it requires zero setup or external server dependencies.

### 1. Database File
The database is stored in a single, local file in your project root:
- **File Name**: `db.sqlite3`
- **Location**: `d:\placement-manage\db.sqlite3`

### 2. Django Configuration
The connection is established in `placement_portal/settings.py` within the `DATABASES` dictionary:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3. Database Migrations
Whenever you modify your database models in `core/models.py`, you must update the database schema using migrations:
- **Generate Migration Files**:
  ```bash
  python manage.py makemigrations
  ```
- **Apply Migrations to SQLite**:
  ```bash
  python manage.py migrate
  ```

---

## 🔑 Admin Section (Django Admin Panel)

The Django Admin is a powerful, built-in interface for managing all database tables (Students, Jobs, Applications, and Users).

### 1. Access the Admin Panel
Navigate to:
👉 **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

### 2. Default Credentials
We have pre-configured a Superuser account for you:
- **Username**: `admin`
- **Password**: `admin123` *(You can change this password inside the admin panel or via the command line)*

### 3. Creating a New Admin/Superuser
If you ever want to create another admin account, run:
```bash
python manage.py createsuperuser
```
Follow the interactive prompts to set a new username, email, and password.

---

## 📂 Project Architecture

```
placement-manage/
│
├── core/                       # Core application logic
│   ├── models.py               # StudentProfile, JobPosting, Application
│   ├── views.py                # Student/Company dashboard views, login, registration
│   ├── urls.py                 # Core app page routes
│   └── templates/core/         # HTML templates (Bootstrap 5)
│       ├── base.html           # Main layout and navbar
│       ├── home.html           # Welcome home page
│       ├── login.html          # Authentication login
│       ├── register.html       # Student registration form
│       ├── student_dashboard.html  # Student application pipeline
│       └── company_dashboard.html  # Recruiter dashboard
│
├── placement_portal/           # Main project configuration
│   ├── settings.py             # Database config, installed apps, static/media files
│   ├── urls.py                 # Root URL router (includes core URLs)
│   └── wsgi.py / asgi.py       # WSGI/ASGI server configs
│
├── media/resumes/              # Directory for uploaded resumes
├── db.sqlite3                  # SQLite Database file
└── manage.py                   # Django management utility script
```

---

## 🌟 Next Development Steps

Now that you know how to run the project, here are some recommended enhancements:
1. **Premium Theme Integration**: Update CSS and template cards to support modern dark/light mode and beautiful modern glassmorphism.
2. **Seed Mock Data**: Generate realistic jobs and mock students to view the portal fully populated.
3. **Advanced Eligibility Check**: Add validation to prevent students below the required CGPA or from ineligible branches from applying to specific jobs.
