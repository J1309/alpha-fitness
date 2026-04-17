from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os
import io
import re
from datetime import datetime
from functools import wraps
import qrcode
import bleach

app = Flask(__name__)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'alpha-fitness-session-key-2026')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Database path
DATABASE = os.path.join(os.path.dirname(__file__), 'user_entries.db')

# Admin password
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Anil007')


def sanitize_input(text, max_length=500):
    """Sanitize user input to prevent XSS"""
    if text is None:
        return ''
    text = str(text).strip()
    text = bleach.clean(text, tags=[], strip=True)
    return text[:max_length]


def get_db():
    """Connect to SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database and create table if not exists"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            interest TEXT,
            message TEXT,
            payment_status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


init_db()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# CSRF Form for Admin Login
class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Login')


# CSRF Form for Contact/Join Form
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=5, max=20)])
    interest = StringField('Interest', validators=[DataRequired()])
    submit = SubmitField('Submit')


reviews = [
    {
        "name": "DAVID ZACHARIAH PRASAD",
        "text": "Such an excellent Gym in Kerala. The Staffs and Trainers are very friendly, will have good workout sessions with Alpha.",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": True
    },
    {
        "name": "Dhuaa Manzoor",
        "text": "Alpha fit provides a very welcoming and a peaceful environment for workouts. The place is very artistic which makes it an attraction and the services are too good to mention.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "S Uma Sankar",
        "text": "Well equipped and perfectly spaced gym. Trainers are professionally experienced. The Vibe is motivational enough to push your limits everyday.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "lijin john",
        "text": "Was looking for a gym to workout for few days.. checked out few places and man this one lives up to the expectation. Decently equipped for weight training and cardio / HIIT. Highly recommended.",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": False
    },
    {
        "name": "Mahesh S Nair",
        "text": "It's well maintained and clean. The gym community is also good here. It's a healthy environment.",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": True
    },
    {
        "name": "ABHIRAJ SATHEESH",
        "text": "Trainers are highly professional and experienced trainers. Best gym in pathanamthitta.",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False
    },
    {
        "name": "NISAM NAZER",
        "text": "Wonderfull experience.very friendly trainer.overall feedback is awesome.",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False
    },
    {
        "name": "Restina Thomas",
        "text": "Best trainers and best gym in town.. worth it.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Alen Mathew",
        "text": "Themost beautiful gym ever sawed",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False
    },
    {
        "name": "Abdu Salam Thalappally",
        "text": "Nice family friendly gym",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Arjun Sajikumar",
        "text": "Really nice gym with qualified trainers.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Aravind Chandran",
        "text": "Super gym and the trainers.. Just cool...",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": True
    },
    {
        "name": "Sooraj Rk",
        "text": "Great gym",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Dr Prasanth Sankar",
        "text": "Best gym in town",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": False
    },
    {
        "name": "Prince Kallukalam",
        "text": "Professional Gym I like it",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": True
    },
    {
        "name": "Shivadath Jayaraj",
        "text": "The best in Town.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Sreedhu Mahesh",
        "text": "Good",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": True
    },
    {
        "name": "Ammini Daniel",
        "text": "Love it!",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Sini Sabu",
        "text": "Amazing!",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Alan Mamachan",
        "text": "Its amazing",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    },
    {
        "name": "Aswin",
        "text": "Great gym with a solid atmosphere. The equipment is well-maintained, and there's a good variety of machines and free weights. It stays clean even during busy hours. The staff is friendly and always willing to help. Highly recommend for anyone in the area looking for a consistent place to train.",
        "stars": 5,
        "time": "a day ago",
        "is_local_guide": False
    },
    {
        "name": "Alfin Ninan",
        "text": "Good atmosphere and well trained trainers and friendly people.",
        "stars": 5,
        "time": "4 days ago",
        "is_local_guide": False
    },
    {
        "name": "Ragen 10",
        "text": "Excellent facility! Clean environment, plenty of equipment, and a great vibe for working out. Definitely one of the better gyms I've been to.",
        "stars": 5,
        "time": "4 days ago",
        "is_local_guide": False
    },
    {
        "name": "Dhaannn",
        "text": "Gym is very nice and great.",
        "stars": 5,
        "time": "4 days ago",
        "is_local_guide": False
    },
    {
        "name": "Chris",
        "text": "Good experience",
        "stars": 5,
        "time": "4 days ago",
        "is_local_guide": False
    },
    {
        "name": "Cecil Mandapathil Casablanca",
        "text": "Very good gym in Pathanamthitta for family. Better equipments compared to other gyms in Pathanamthitta.",
        "stars": 5,
        "time": "2 weeks ago",
        "is_local_guide": True
    },
    {
        "name": "Ritwika Manoj",
        "text": "Very friendly trainers and friendly atmosphere. Good service.",
        "stars": 5,
        "time": "a month ago",
        "is_local_guide": False
    },
    {
        "name": "Akhil Mohan",
        "text": "Definitely the best gym in Pathanamthitta!",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": True
    },
    {
        "name": "Joshua Mavelil",
        "text": "The perfect place for exercise. A welcoming atmosphere, expert staff...",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": False
    },
    {
        "name": "Soul Sayshi",
        "text": "Best gym in Pathanamthitta",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False
    },
    {
        "name": "Sangeeth S",
        "text": "A good fitness center is more than just a place to exercise; it is a motivating and supportive environment where people work towards a healthier lifestyle. It is clean, spacious, and well-equipped with modern machines and quality workout.",
        "stars": 5,
        "time": "a month ago",
        "is_local_guide": False
    },
    {
        "name": "Mahadev Mahi",
        "text": "The gym was soo nice and such a great ambiance. The trainers are soo supportive. This gym don't have any age restriction. Once we came here to workout we never skip a day for cheating. I like this gym soo much.",
        "stars": 5,
        "time": "a month ago",
        "is_local_guide": False
    },
    {
        "name": "Tintu john abraham",
        "text": "Alpha Club is one of the best fitness for beginners and pro members. Well equipped instruments and pro active approach of trainers. Spacious neat and clean fitness centre in Pathanamthitta.",
        "stars": 5,
        "time": "a month ago",
        "is_local_guide": True
    },
    {
        "name": "Renju George Thoppil",
        "text": "If you want to have a premium experience of a Health Club at the heart of Pathanamthitta, with Quality oriented machines, equipment and trainers who have completed their NASM certification then Alpha Fitness is your next stop. The Health Club is equipped with world class equipment.",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": True
    },
    {
        "name": "Ameer Muhammed",
        "text": "The gym is very awesom. The trainers are very supporting and very helping trainers. The training is very nice and amzing ambience. I love this gym.",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False
    },
    {
        "name": "Aswin S Panicker",
        "text": "One of the best equipped air conditioned gym in Pathanamthitta. Trainers are very experienced and will help you reach your goals and do so scientifically.",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": True
    },
    {
        "name": "Jeevan Prakash",
        "text": "If you want to be in a premium fitness centre, go and start a new fitness journey to achieve your goal.",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": False
    },
    {
        "name": "Alan Varghese",
        "text": "Impressive gym with top-notch equipment and a clean, inviting atmosphere. Friendly staff and convenient hours make it a standout choice for anyone seeking a quality workout experience. Highly recommend!",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": False
    },
    {
        "name": "Sonia Prathap",
        "text": "Exercise should be regarded as a Tribute to our Body. Of all the paths you step in Life, make sure to take a few steps towards Alpha Fitness. Why?? Because, The Quality of the Equipments, The Safety and Comfort, The Availability of Modern Amenities, Aesthetic Appeal of the Facility and Above all Friendly Attitude of Professionally Experienced Staff makes Alpha Fitness a Perfect Place for Workouts.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False
    }
]

trainers = [
    {"name": "Anil Sam Joseph", "title": "Head Trainer & Owner", "bio": "Strength & Conditioning specialist.",
     "image": "/static/assets/trainers/anil.png"},
    {"name": "Sajith", "title": "Trainer", "bio": "Personal Training expert.",
     "image": "/static/assets/trainers/sajith.png"},
    {"name": "Ashna", "title": "Co-Trainer", "bio": "Mobility & Endurance expert.",
     "image": "/static/assets/trainers/ashna.png"},
]

gallery = [
    {"src": "/static/assets/gallery/2023-03-26.webp", "alt": "Gym Equipment"},
    {"src": "/static/assets/gallery/2022-10-19.webp", "alt": "Training Session"},
    {"src": "/static/assets/gallery/2023-01-17.webp", "alt": "Workout Area"},
    {"src": "/static/assets/gallery/2024-01-06.webp", "alt": "Fitness Training"},
    {"src": "/static/assets/gallery/2026-03-08.webp", "alt": "Alpha Fitness"},
    {"src": "/static/assets/gallery/IMG-20211211-WA0291.webp", "alt": "Gym Interior"},
    {"src": "/static/assets/gallery/SAVE_20211204_200102.webp", "alt": "Training"},
    {"src": "/static/assets/gallery/unnamed.webp", "alt": "Fitness Center"},
    {"src": "/static/assets/gallery/unnamed (1).webp", "alt": "Workout"},
    {"src": "/static/assets/gallery/unnamed (2).webp", "alt": "Gym Equipment"},
    {"src": "/static/assets/gallery/unnamed (3).webp", "alt": "Training Area"},
    {"src": "/static/assets/gallery/unnamed (4).webp", "alt": "Alpha Gym"},
    {"src": "/static/assets/gallery/unnamed (5).webp", "alt": "Fitness Club"},
    {"src": "/static/assets/gallery/new img1.jpeg", "alt": "Alpha Fitness"},
    {"src": "/static/assets/gallery/new img2.jpeg", "alt": "Gym Training"},
    {"src": "/static/assets/gallery/new img3.jpeg", "alt": "Workout Session"},
    {"src": "/static/assets/gallery/new img4.jpeg", "alt": "Fitness Center"},
]


@app.route("/")
def home():
    return render_template("home.html", trainers=trainers, gallery=gallery, reviews=reviews)


@app.route('/imgs/<path:filename>')
def serve_imgs(filename):
    root = os.path.join(app.root_path, 'imgs')
    return send_from_directory(root, filename)


@app.route("/reviews")
def reviews_page():
    return render_template("reviews.html", reviews=reviews)


@app.route("/gallery")
def gallery_page():
    return render_template("gallery.html", trainers=trainers, gallery=gallery)


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/submit", methods=["POST"])
def submit_entry():
    name = sanitize_input(request.form.get("name"), 100)
    phone = sanitize_input(request.form.get("phone"), 20)
    interest = sanitize_input(request.form.get("interest"), 50)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not name or not phone or not interest:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("contact_page"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (name, email, phone, interest, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, None, phone, interest, None, created_at))
    conn.commit()
    conn.close()

    flash("Thank you! We'll contact you soon.", "success")
    return redirect(url_for("contact_page"))


@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect password. Please try again.", "error")
    return render_template("admin_login.html", form=form)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
    entries = cursor.fetchall()
    conn.close()

    total_entries = len(entries)

    return render_template("admin_dashboard.html",
                           entries=entries,
                           total_entries=total_entries)


@app.route("/admin/qr")
def admin_qr_page():
    return render_template("admin_qr.html")


@app.route("/qr-image")
def qr_image():
    url = request.url_root.rstrip('/') + url_for('admin_login')
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


@app.route("/admin/delete/<int:entry_id>", methods=["POST"])
@admin_required
def delete_entry(entry_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.errorhandler(429)
def ratelimit_handler(e):
    flash("Too many attempts. Please wait a minute and try again.", "error")
    return redirect(url_for("admin_login")), 429


if __name__ == "__main__":
    app.run(debug=True)
