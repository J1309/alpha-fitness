from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import os
import io
from datetime import datetime
from functools import wraps
import qrcode

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'alpha-fitness-secret-key-2026')

# Database path
DATABASE = os.path.join(os.path.dirname(__file__), 'user_entries.db')

# Admin password - CHANGE THIS TO YOUR DESIRED PASSWORD
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'alpha2026')

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

# Initialize database on startup
init_db()

# Decorator for admin login
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

reviews = [
    {
        "name": "Sangeeth S",
        "text": "A good fitness center is more than just a place to exercise; it is a motivating and supportive environment where people work towards a healthier lifestyle. It is clean, spacious, and well-equipped with modern machines and quality workout.",
        "stars": 5,
        "time": "a month ago",
        "is_local_guide": False
    },
    {
        "name": "Mahadev Mahi",
        "text": "The gym was soo nice and such a great ambiance. The trainers are soo supportive. This gym don't have any age restriction. Once we came here to workout we never skip a day for cheating. I like this gym soo much. Everyone should visit and take there workout here.",
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
        "name": "Ronak Roy",
        "text": "Alpha Fitness Club is an amazing gym with top-notch equipment and fantastic trainers! The staff is friendly and knowledgeable, and the atmosphere is always motivating and supportive. I've seen great results since joining, and I highly recommend it to anyone looking to achieve their fitness goals.",
        "stars": 5,
        "time": "8 months ago",
        "is_local_guide": False,
        "photos": True
    },
    {
        "name": "Renju George Thoppil",
        "text": "If you want to have a premium experience of a Health Club at the heart of Pathanamthitta, with Quality oriented machines, equipment and trainers who have completed their NASM certification then Alpha Fitness is your next stop. The Health Club is equipped with world class equipment and the staff will guide you with care to learn and breakdown movements to smaller achievable results. You can go on a regular day either in the morning or evening and come across a community of people who workout together like a family in a mild manner.",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": True,
        "photos": True
    },
    {
        "name": "Ameer Muhammed",
        "text": "The gym is very awesom. The trainers Aju bro, Sheyas bro and Alan bro. They are very supporting and very helping trainers. The training is very nice and amzing ambience. I love this gym. I would recommend everyone to join this gym.",
        "stars": 5,
        "time": "a year ago",
        "is_local_guide": False,
        "photos": True
    },
    {
        "name": "Aswin S Panicker",
        "text": "One of the best equipped air conditioned gym in Pathanamthitta. Trainers are very experienced and will help you reach your goals and do so scientifically.",
        "stars": 5,
        "time": "2 years ago",
        "is_local_guide": True,
        "photos": True
    },
    {
        "name": "Jeevan Prakash",
        "text": "If you want to be in a premium fitness centre, go and start a new fitness journey to achieve your goal.",
        "stars": 5,
        "time": "4 years ago",
        "is_local_guide": False,
        "photos": True
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
        "text": "Exercise should be regarded as a Tribute to our Body. Of all the paths you step in Life, make sure to take a few steps towards Alpha Fitness. Why?? Because, The Quality of the Equipments, The Safety and Comfort, The Availability of Modern Amenities, Aesthetic Appeal of the Facility and Above all Friendly Attitude of Professionally Experienced Staff makes Alpha Fitness a Perfect Place for Workouts. The Best Gym... Ever Seen in Pathanamthitta.",
        "stars": 5,
        "time": "3 years ago",
        "is_local_guide": False,
        "photos": True
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
    {"src": "/static/assets/gallery/2024-01-06 (1).webp", "alt": "Gym Session"},
    {"src": "/static/assets/gallery/2026-03-08.webp", "alt": "Alpha Fitness"},
    {"src": "/static/assets/gallery/IMG-20211211-WA0291.webp", "alt": "Gym Interior"},
    {"src": "/static/assets/gallery/SAVE_20211204_200102.webp", "alt": "Training"},
    {"src": "/static/assets/gallery/unnamed.webp", "alt": "Fitness Center"},
    {"src": "/static/assets/gallery/unnamed (1).webp", "alt": "Workout"},
    {"src": "/static/assets/gallery/unnamed (2).webp", "alt": "Gym Equipment"},
    {"src": "/static/assets/gallery/unnamed (3).webp", "alt": "Training Area"},
    {"src": "/static/assets/gallery/unnamed (4).webp", "alt": "Alpha Gym"},
    {"src": "/static/assets/gallery/unnamed (5).webp", "alt": "Fitness Club"},
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
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    interest = request.form.get("interest")
    message = request.form.get("message")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (name, email, phone, interest, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, interest, message, created_at))
    conn.commit()
    conn.close()
    
    flash("Thank you! We'll contact you soon.", "success")
    return redirect(url_for("contact_page"))

# Admin Routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect password. Please try again.", "error")
    return render_template("admin_login.html")

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
    pending_count = len([e for e in entries if e["payment_status"] == "pending"])
    paid_count = len([e for e in entries if e["payment_status"] == "paid"])
    
    return render_template("admin_dashboard.html", 
                           entries=entries, 
                           total_entries=total_entries,
                           pending_count=pending_count,
                           paid_count=paid_count)

@app.route("/admin/update-status/<int:entry_id>", methods=["POST"])
@admin_required
def update_status(entry_id):
    new_status = request.form.get("payment_status")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET payment_status = ? WHERE id = ?", (new_status, entry_id))
    conn.commit()
    conn.close()
    flash(f"Payment status updated to {new_status}.", "success")
    return redirect(url_for("admin_dashboard"))

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

if __name__ == "__main__":
    app.run(debug=True)
