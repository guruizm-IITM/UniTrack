# 🎓 UniTrack — Student & Course Management System

UniTrack is a lightweight, elegant, and fully functional web application built using **Flask** and **SQLAlchemy**. It enables seamless management of **students**, **courses**, and **enrollments** with a clean, modern **dark-themed UI** powered by **Bootstrap 5**.

This project is ideal for beginners learning Flask, as well as developers who want a minimal, extendable academic management system.

---

## 🚀 Features

### 👨‍🎓 Student Management
- Create, update, view, and delete students  
- Unique roll number enforcement  
- View individual student profiles  
- Enroll or withdraw students from courses  

### 📚 Course Management
- Create, update, view, and delete courses  
- Unique course code enforcement  
- View enrolled students in any course  

### 🔗 Enrollment System
- Many-to-many relationship using an `enrollments` table  
- Add or remove course enrollments from the student’s profile page  

### 🎨 Dark-Themed UI
- Fully responsive interface  
- Beautiful Bootstrap 5 styling  
- Consistent UniTrack branding across all templates  

### 💾 Database
- SQLite-powered storage using SQLAlchemy ORM  
- Auto-generated tables  
- Clean models with relationships  

---

## 🔧 Tech Stack

| Component | Technology |
|----------|------------|
| Backend Framework | Flask |
| ORM | SQLAlchemy |
| Database | SQLite |
| Frontend | HTML5, Jinja2, Bootstrap 5 |
| Styling | Custom Dark Theme |

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/unitrack.git
cd unitrack
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate           # Linux / macOS
venv\Scripts\activate            # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Your UniTrack app will be available at:

```
http://127.0.0.1:5000/
```

---

## 📁 Project Structure

```
UniTrack/
│
├── app.py                # Main Flask application
├── database.sqlite3      # SQLite database (auto-created)
├── templates/            # HTML templates
├── static/               # CSS/JS (optional)
└── requirements.txt      # Dependencies
```

---

## 🧩 Key Design Highlights

### ✔ Clean Routing  
Each CRUD operation has its own clear route (e.g., `/student/create/`, `/course/update/`, etc.).

### ✔ SQLAlchemy Models  
- `Student`
- `Course`
- `Enrollments` (junction table)  
With clear foreign keys and relationships.

### ✔ No Breaking Behavior  
Every enhancement preserves original logic and intended flow.

---

## 🛠 Future Improvements

These would be great enhancements if you want to grow the project:

- Authentication (Admin login)
- Search & filter for students/courses
- Pagination for large datasets
- CSV import/export for bulk management
- Attendance or grading modules

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, open an issue first to discuss your ideas.

---

## 📜 License

This project is licensed under the **MIT License** — free for personal and commercial use.

---

## ⭐ Acknowledgments

Built with ❤️ using:
- Flask  
- SQLAlchemy  
- Bootstrap 5  
- A beautifully crafted dark UI for the UniTrack brand  
