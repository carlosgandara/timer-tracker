# models.py – Timer Tracker (Simplified)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), nullable=False)
    activity = db.Column(db.String(50), nullable=True)
    duration = db.Column(db.Integer, nullable=False)  # seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ColorMap(db.Model):
    __tablename__ = "color_maps"
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), unique=True, nullable=False)
    hex_code = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(50), unique=True, nullable=False)
    is_gradient = db.Column(db.Boolean, default=False)

# NEW: Persistent Timer Session
class TimerSession(db.Model):
    __tablename__ = "timer_sessions"
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), nullable=False)
    activity = db.Column(db.String(50), nullable=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    # If you add user auth later, add user_id here