from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from models import db, Log, ColorMap
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()
    if ColorMap.query.count() == 0:
        defaults = [
            ("blue", "Work"),
            ("green", "Rest"),
            ("red", "Exercise"),
            ("yellow", "Social"),
            ("purple", "Creative"),
            ("orange", "Meal"),
            ("white", "Neutral"),
            ("black", "Sleep"),
        ]
        for color, activity in defaults:
            db.session.add(ColorMap(color=color, activity=activity))
        db.session.commit()

@app.route("/")
def index():
    colors = ColorMap.query.all()
    return render_template("index.html", colors=colors)

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json()
    color = data.get("color")
    duration = data.get("duration")
    if not color or duration is None:
        return jsonify({"error": "Missing color or duration"}), 400
    color_map = ColorMap.query.filter_by(color=color).first()
    activity = color_map.activity if color_map else color
    log_entry = Log(color=color, activity=activity, duration=int(duration))
    db.session.add(log_entry)
    db.session.commit()
    return jsonify({"success": True, "log_id": log_entry.id})

@app.route("/dashboard")
def dashboard():
    today = datetime.now().date()
    week_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    week_start = week_days[0]
    week_end = week_days[-1] + timedelta(days=1)
    logs = Log.query.filter(
        Log.timestamp >= week_start,
        Log.timestamp < week_end
    ).order_by(Log.timestamp.asc()).all()

    days_data = {}
    for day in week_days:
        day_str = day.strftime("%Y-%m-%d")
        days_data[day_str] = {"date": day.strftime("%A, %B %d"), "logs": []}
    for log in logs:
        day_str = log.timestamp.strftime("%Y-%m-%d")
        if day_str in days_data:
            days_data[day_str]["logs"].append({
                "time": log.timestamp.strftime("%I:%M %p"),
                "color": log.color,
                "activity": log.activity,
                "duration": log.duration,
                "duration_min": round(log.duration / 60, 1),
            })

    summary = defaultdict(int)
    for log in logs:
        summary[log.color] += log.duration
    summary_list = []
    total_seconds = sum(summary.values())
    for color, seconds in sorted(summary.items(), key=lambda x: x[1], reverse=True):
        minutes = round(seconds / 60)
        hours = round(minutes / 60, 1)
        display = f"{hours}h" if hours >= 1 else f"{minutes}m"
        percentage = round((seconds / total_seconds) * 100) if total_seconds > 0 else 0
        summary_list.append({
            "color": color,
            "display": display,
            "percentage": percentage,
            "minutes": minutes,
        })
    total_hours = round(total_seconds / 3600, 1) if total_seconds > 0 else 0
    return render_template("dashboard.html", days=days_data, summary=summary_list, total_hours=total_hours)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("color_"):
                color = key.replace("color_", "")
                activity = value.strip()
                if activity:
                    color_map = ColorMap.query.filter_by(color=color).first()
                    if color_map:
                        color_map.activity = activity
                        db.session.commit()
        return redirect(url_for("settings"))
    colors = ColorMap.query.order_by(ColorMap.id).all()
    return render_template("settings.html", colors=colors)

@app.route("/api/logs/<date>")
def get_logs_by_date(date):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        next_day = target_date + timedelta(days=1)
        logs = Log.query.filter(
            Log.timestamp >= target_date,
            Log.timestamp < next_day
        ).order_by(Log.timestamp.asc()).all()
        data = []
        for log in logs:
            data.append({
                "time": log.timestamp.strftime("%I:%M %p"),
                "color": log.color,
                "activity": log.activity,
                "duration_min": round(log.duration / 60, 1),
                "duration_seconds": log.duration,
            })
        return jsonify(data)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
