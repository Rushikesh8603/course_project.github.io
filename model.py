

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    influencer_signups = db.relationship('InfluencerSignup', backref='user', lazy=True)
    sponsor_signups = db.relationship('SponsorSignup', backref='user', lazy=True)
    Request_for_sponsor = db.relationship('request_for_sponsor', backref='user', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  


class InfluencerSignup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class SponsorSignup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class request_for_sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    #this  user_id means the influensor details who have requsted 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    status = db.Column(db.String(20), nullable=False, default='Pending')
    #this is a user_id of the campain who have created
    camp_user_id = db.Column(db.Integer)


