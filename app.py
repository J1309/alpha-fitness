from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

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
     "image": "/static/assets/trainers/jordan.svg"},
    {"name": "Sajith", "title": "Trainer", "bio": "Personal Training expert.",
     "image": "/static/assets/trainers/sam.svg"},
    {"name": "Ashna", "title": "Co-Trainer", "bio": "Mobility & Endurance expert.",
     "image": "/static/assets/trainers/ashna.svg"},
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

# Serve additional image assets from an 'imgs' folder at project root for logos and similar
@app.route('/imgs/<path:filename>')
def serve_imgs(filename):
    # Serve from the 'imgs' directory located in the project
    root = os.path.join(app.root_path, 'imgs')
    # Normalize path to avoid directory traversal in some environments
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

if __name__ == "__main__":
    app.run(debug=True)
