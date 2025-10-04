import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ------------------ App Config ------------------
app = Flask(__name__)
app.secret_key = "greenTechSecret"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///footprints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ------------------ Models ------------------
class Footprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    electricity = db.Column(db.Float, nullable=False)
    water = db.Column(db.Float, nullable=False)
    travel = db.Column(db.Float, nullable=False)
    waste = db.Column(db.Float, nullable=False)
    total_co2 = db.Column(db.Float, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)


class GameScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_played = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('index.html', hide_hero=False)


@app.route('/donate')
def donate():
    return render_template('donate.html', hide_hero=False)


@app.route('/about')
def about():
    return render_template('about.html', hide_hero=False)


@app.route('/citations')
def citations():
    return render_template('citations.html', hide_hero=False)


@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html', hide_hero=False)


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        name = request.form.get('name')
        score = int(request.form.get('score', 0))
        if name:
            new_score = GameScore(name=name, score=score)
            db.session.add(new_score)
            db.session.commit()
            flash("Your score has been saved!")
        return redirect(url_for('game'))

    leaderboard = GameScore.query.order_by(GameScore.score.desc()).limit(5).all()
    return render_template('game.html', hide_hero=True, leaderboard=leaderboard)


@app.route('/tutorials/e-waste-management')
def e_waste_management():
    return render_template('e_waste_management.html', hide_hero=False)


@app.route('/tutorials/energy-efficiency')
def energy_efficiency():
    return render_template('energy_efficiency.html', hide_hero=False)


@app.route('/tutorials/sustainable-hardware')
def sustainable_hardware():
    return render_template('sustainable_hardware.html', hide_hero=False)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"New Feedback - Name: {name}, Email: {email}, Message: {message}")
        flash("Thank you for your feedback!")
        return redirect(url_for('contact'))
    return render_template('contact.html', hide_hero=False)


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    if request.method == 'POST':
        name = request.form.get('name')
        electricity = float(request.form.get('electricity', 0))
        water = float(request.form.get('water', 0))
        travel = float(request.form.get('travel', 0))
        waste = float(request.form.get('waste', 0))

        # CO2 Calculations
        co2_electricity = electricity * 0.82
        co2_water = water * 0.0003
        co2_travel = travel * 0.21
        co2_waste = waste * 1.9

        total_co2 = round(co2_electricity + co2_water + co2_travel + co2_waste, 2)

        # Save to DB
        new_entry = Footprint(
            name=name,
            electricity=electricity,
            water=water,
            travel=travel,
            waste=waste,
            total_co2=total_co2
        )
        db.session.add(new_entry)
        db.session.commit()

        flash("Your footprint has been calculated and saved!")
        result = total_co2

    history = Footprint.query.order_by(Footprint.total_co2.asc()).limit(5).all()
    return render_template('calculator.html', result=result, history=history)


# ------------------ Run ------------------

# ---- DB URI: prefer DATABASE_URL (Render Postgres), fallback to local SQLite ----
db_uri = os.getenv('DATABASE_URL', 'sqlite:///footprints.db')
# modern SQLAlchemy expects 'postgresql://' not 'postgres://'
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------- after your model classes -------------
# Ensure tables exist on startup (safe for small projects)
with app.app_context():
    db.create_all()

