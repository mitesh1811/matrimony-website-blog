from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_master = db.Column(db.Boolean, default=False)
    
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    caste = db.Column(db.String(50), nullable=True)
    religion = db.Column(db.String(50), nullable=True)
    mother_tongue = db.Column(db.String(50), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    income = db.Column(db.String(50), nullable=True)
    diet = db.Column(db.String(50), nullable=True)
    smoking = db.Column(db.String(20), nullable=True)
    drinking = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    photo_filename = db.Column(db.String(100), nullable=True)



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
