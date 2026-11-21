"""
ACEest Fitness & Gym Management System - Version 1.0.0
Base foundational Flask web application.
Migrated from desktop Tkinter prototype to web architecture.
"""

from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aceest-secret-v1'

VERSION = os.environ.get("APP_VERSION", "1.0.0")

# Core fitness program specifications from Aceestver-1.0
PROGRAMS = {
    "Fat Loss (FL)": {
        "id": "FL",
        "name": "Fat Loss (FL)",
        "workout": "Mon: 5x5 Back Squat + AMRAP | Tue: EMOM 20min Assault Bike | Wed: Bench Press + 21-15-9 | Thu: 10RFT Deadlifts/Box Jumps | Fri: 30min Active Recovery",
        "diet": "Breakfast: 3 Egg Whites + Oats Idli | Lunch: Grilled Chicken + Brown Rice | Dinner: Fish Curry + Millet Roti | Target: 2,000 kcal",
        "target_calories": 2000,
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "id": "MG",
        "name": "Muscle Gain (MG)",
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "Breakfast: 4 Eggs + PB Oats | Lunch: Chicken Biryani (250g Chicken) | Dinner: Mutton Curry + Jeera Rice | Target: 3,200 kcal",
        "target_calories": 3200,
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "id": "BG",
        "name": "Beginner (BG)",
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups. Focus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Traditional Meals: Idli-Sambar, Rice-Dal, Chapati. Protein: 120g/day",
        "target_calories": 2200,
        "color": "#3498db"
    }
}

HTML_TEMPLATE_V1 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ACEest Functional Fitness v{{ version }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: #fff; margin: 0; padding: 0; }
        header { background: #d4af37; color: #000; padding: 20px; text-align: center; }
        h1 { margin: 0; font-size: 26px; }
        .version-tag { display: inline-block; background: #000; color: #d4af37; padding: 4px 10px; border-radius: 4px; font-size: 14px; margin-top: 5px; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: #242424; border: 1px solid #333; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card h2 { color: #d4af37; margin-top: 0; }
        .prog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .prog-card { background: #2f2f2f; border-left: 4px solid #d4af37; padding: 15px; border-radius: 4px; }
        .prog-card h3 { margin-top: 0; color: #fff; }
        .footer { text-align: center; color: #777; font-size: 13px; margin: 40px 0; }
    </style>
</head>
<body>
    <header>
        <h1>ACEest FUNCTIONAL FITNESS & GYM</h1>
        <div class="version-tag">Release v{{ version }}</div>
    </header>
    <div class="container">
        <div class="card">
            <h2>Core Fitness & Nutrition Programs</h2>
            <div class="prog-grid">
                {% for key, prog in programs.items() %}
                <div class="prog-card" style="border-left-color: {{ prog.color }};">
                    <h3>{{ prog.name }}</h3>
                    <p><strong>Workout:</strong> {{ prog.workout }}</p>
                    <p><strong>Diet:</strong> {{ prog.diet }}</p>
                    <p><strong>Target:</strong> {{ prog.target_calories }} kcal</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="footer">ACEest Fitness DevOps Assignment - v{{ version }}</div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE_V1, programs=PROGRAMS, version=VERSION)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "aceest-fitness",
        "version": VERSION
    }), 200

@app.route('/ready')
def ready():
    return jsonify({
        "ready": True,
        "version": VERSION
    }), 200

@app.route('/version')
def version():
    return jsonify({
        "version": VERSION
    }), 200

@app.route('/api/programs', methods=['GET'])
def get_programs():
    return jsonify(PROGRAMS), 200

@app.route('/api/calculate-calories', methods=['POST'])
def calculate_calories():
    data = request.get_json() or {}
    program = data.get('program', 'Beginner (BG)')
    weight = float(data.get('weight', 70))
    
    base_calories = PROGRAMS.get(program, {}).get('target_calories', 2000)
    adjusted_calories = round(base_calories * (weight / 70.0))
    
    return jsonify({
        "program": program,
        "weight_kg": weight,
        "recommended_calories": adjusted_calories
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
