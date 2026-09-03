from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import Config
from models import db, Log, ColorMap, TimerSession
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()
    if ColorMap.query.count() == 0:
        defaults = [
            ("blue", "#4f8cf7", "Work", False),
            ("green", "#38a169", "Rest", False),
            ("red", "#e53e3e", "Exercise", False),
            ("yellow", "#ecc94b", "Social", False),
            ("purple", "#9f7aea", "Creative", False),
            ("orange", "#ed8936", "Meal", False),
            ("white", "#e2e8f0", "Neutral", False),
            ("black", "#2d3748", "Sleep", False),
        ]
        for color, hex_code, activity, is_gradient in defaults:
            db.session.add(ColorMap(
                color=color,
                hex_code=hex_code,
                activity=activity,
                is_gradient=is_gradient
            ))
        db.session.commit()

# ---------- Routes ----------

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
    offset_minutes = request.args.get("offset", 0, type=int)
    week_param = request.args.get("week")
    year_param = request.args.get("year")

    now_utc = datetime.utcnow()
    now_local = now_utc + timedelta(minutes=offset_minutes)

    try:
        selected_week = int(week_param) if week_param else now_local.isocalendar()[1]
        selected_year = int(year_param) if year_param else now_local.year
        if selected_week < 1 or selected_week > 53:
            selected_week = now_local.isocalendar()[1]
            selected_year = now_local.year
    except (ValueError, TypeError):
        selected_week = now_local.isocalendar()[1]
        selected_year = now_local.year

    jan4 = datetime(selected_year, 1, 4)
    days_to_monday = (jan4.weekday() - 0) % 7
    monday_week1 = jan4 - timedelta(days=days_to_monday)
    monday_local = monday_week1 + timedelta(weeks=selected_week - 1)
    sunday_local = monday_local + timedelta(days=6)

    monday_utc = monday_local - timedelta(minutes=offset_minutes)
    sunday_utc = sunday_local - timedelta(minutes=offset_minutes) + timedelta(days=1)

    logs = Log.query.filter(
        Log.timestamp >= monday_utc,
        Log.timestamp < sunday_utc
    ).order_by(Log.timestamp.asc()).all()

    days_data = {}
    for i in range(7):
        day = monday_local + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        days_data[day_str] = {
            "date": day.strftime("%A, %B %d"),
            "logs": []
        }

    for log in logs:
        log_local = log.timestamp - timedelta(minutes=offset_minutes)
        day_str = log_local.strftime("%Y-%m-%d")
        if day_str in days_data:
            color_map = ColorMap.query.filter_by(color=log.color).first()
            hex_code = color_map.hex_code if color_map else "#cccccc"
            days_data[day_str]["logs"].append({
                "time": log_local.strftime("%I:%M %p"),
                "color": log.color,
                "hex_code": hex_code,
                "activity": log.activity,
                "duration": log.duration,
                "duration_min": round(log.duration / 60, 1),
            })

    # Compute day totals
    for day_str in days_data:
        day_logs = days_data[day_str]["logs"]
        total_seconds = sum(log["duration"] for log in day_logs)
        days_data[day_str]["total"] = round(total_seconds / 60, 1)

    # Summary
    summary = defaultdict(int)
    for log in logs:
        summary[log.color] += log.duration

    summary_list = []
    total_seconds = sum(summary.values())
    for color, seconds in sorted(summary.items(), key=lambda x: x[1], reverse=True):
        color_map = ColorMap.query.filter_by(color=color).first()
        activity = color_map.activity if color_map else color
        hex_code = color_map.hex_code if color_map else color

        minutes = round(seconds / 60)
        hours = round(minutes / 60, 1)
        display = f"{hours}h" if hours >= 1 else f"{minutes}m"
        percentage = round((seconds / total_seconds) * 100) if total_seconds > 0 else 0
        summary_list.append({
            "color": color,
            "activity": activity,
            "hex_code": hex_code,
            "display": display,
            "percentage": percentage,
            "minutes": minutes,
        })

    total_hours = round(total_seconds / 3600, 1) if total_seconds > 0 else 0
    years = list(range(selected_year - 2, selected_year + 3))

    return render_template(
        "dashboard.html",
        days=days_data,
        summary=summary_list,
        total_hours=total_hours,
        selected_week=selected_week,
        selected_year=selected_year,
        years=years,
        offset=offset_minutes
    )

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add":
            color = request.form.get("color")
            hex_code = request.form.get("hex_code")
            activity = request.form.get("activity")
            is_gradient = request.form.get("is_gradient") == "on"
            
            if color and hex_code and activity:
                existing_activity = ColorMap.query.filter_by(activity=activity).first()
                if existing_activity:
                    flash(f'❌ "{activity}" already exists. Please choose a different name.', "error")
                    return redirect(url_for("settings"))
                
                existing_color = ColorMap.query.filter_by(color=color).first()
                if not existing_color:
                    new_color = ColorMap(
                        color=color,
                        hex_code=hex_code,
                        activity=activity,
                        is_gradient=is_gradient
                    )
                    db.session.add(new_color)
                    db.session.commit()
                    flash(f'✅ "{activity}" added successfully!', "success")
                else:
                    flash(f'❌ Color "{color}" already exists. Please choose a different name.', "error")
        
        elif action == "edit":
            color_id = request.form.get("color_id")
            activity = request.form.get("activity")
            hex_code = request.form.get("hex_code")
            is_gradient = request.form.get("is_gradient") == "on"
            
            color_map = ColorMap.query.get(color_id)
            if color_map:
                existing = ColorMap.query.filter(
                    ColorMap.activity == activity,
                    ColorMap.id != color_id
                ).first()
                if existing:
                    flash(f'❌ "{activity}" already exists. Please choose a different name.', "error")
                    return redirect(url_for("settings"))
                
                color_map.activity = activity
                color_map.hex_code = hex_code
                color_map.is_gradient = is_gradient
                db.session.commit()
                flash(f'✅ "{activity}" updated successfully!', "success")
        
        elif action == "delete":
            color_id = request.form.get("color_id")
            color_map = ColorMap.query.get(color_id)
            if color_map:
                activity_name = color_map.activity
                db.session.delete(color_map)
                db.session.commit()
                flash(f'✅ "{activity_name}" deleted successfully.', "success")
        
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

# ========== PERSISTENT TIMER ROUTES ==========

@app.route("/start", methods=["POST"])
def start_timer():
    """Start a timer session – saves to database."""
    data = request.get_json()
    color = data.get("color")
    
    if not color:
        return jsonify({"error": "Missing color"}), 400
    
    color_map = ColorMap.query.filter_by(color=color).first()
    activity = color_map.activity if color_map else color

    # Clear any previous active session
    TimerSession.query.delete()
    db.session.commit()

    # Create new session
    session = TimerSession(color=color, activity=activity)
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "success": True,
        "start_time": session.start_time.isoformat(),
        "color": session.color,
        "activity": session.activity
    })

@app.route("/stop", methods=["POST"])
def stop_timer():
    """Stop the timer – saves the log and deletes the session."""
    data = request.get_json()
    color = data.get("color")
    duration = data.get("duration")

    if not color or duration is None:
        return jsonify({"error": "Missing color or duration"}), 400

    # Get activity from ColorMap
    color_map = ColorMap.query.filter_by(color=color).first()
    activity = color_map.activity if color_map else color

    # Save the log
    log_entry = Log(color=color, activity=activity, duration=int(duration))
    db.session.add(log_entry)
    db.session.commit()

    # Delete the active session
    TimerSession.query.delete()
    db.session.commit()

    return jsonify({"success": True, "log_id": log_entry.id})

@app.route("/active-timer")
def active_timer():
    """Check if there's an active timer session."""
    session = TimerSession.query.first()
    if session:
        elapsed = (datetime.utcnow() - session.start_time).total_seconds()
        return jsonify({
            "active": True,
            "color": session.color,
            "activity": session.activity,
            "start_time": session.start_time.isoformat(),
            "elapsed_seconds": elapsed
        })
    return jsonify({"active": False})

if __name__ == "__main__":
    app.run(debug=True, port=5000)