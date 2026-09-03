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

    def __repr__(self):
        return f"<Log {self.color} {self.duration}s at {self.timestamp}>"

class ColorMap(db.Model):
    __tablename__ = "color_maps"
    
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), unique=True, nullable=False)  # internal name
    hex_code = db.Column(db.String(50), nullable=False)  # #hex or gradient
    activity = db.Column(db.String(50), unique=True, nullable=False)  # <-- ADD unique=True
    
    is_gradient = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ColorMap {self.color} -> {self.activity}>"


    