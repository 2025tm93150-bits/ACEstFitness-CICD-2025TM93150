"""
ACEest Fitness & Gym Management System - Version 2.0.0
Major upgrade: SQLite database integration, client persistence, and progress tracking.
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aceest-secret-v2-0'

VERSION = os.environ.get("APP_VERSION", "2.0.0")
DB_NAME = os.environ.get("DB_NAME", "aceest_fitness.db")

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

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                target_weight REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                week TEXT,
                adherence INTEGER,
                current_weight REAL,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """)
        # Seed initial sample data if empty
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clients")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, program, target_weight)
                VALUES ('Vikram Seth', 30, 178.0, 84.0, 'Fat Loss (FL)', 75.0)
            """)
            client_id = cur.lastrowid
            cur.execute("""
                INSERT INTO progress (client_id, week, adherence, current_weight)
                VALUES (?, 'Week 1', 90, 83.2)
            """, (client_id,))
            conn.commit()

init_db()

@app.route('/')
def home():
    with get_db() as conn:
        clients = conn.execute("SELECT * FROM clients").fetchall()
    return render_template_string(HTML_TEMPLATE_V2, programs=PROGRAMS, clients=clients, version=VERSION)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "aceest-fitness",
        "version": VERSION
    }), 200

@app.route('/ready')
def ready():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
        return jsonify({
            "ready": True,
            "database": "connected",
            "version": VERSION
        }), 200
    except Exception as e:
        return jsonify({
            "ready": False,
            "error": str(e),
            "version": VERSION
        }), 503

@app.route('/version')
def version():
    return jsonify({
        "version": VERSION
    }), 200

@app.route('/api/programs', methods=['GET'])
def get_programs():
    return jsonify(PROGRAMS), 200

@app.route('/api/clients', methods=['GET', 'POST'])
def manage_clients():
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        age = int(data.get('age', 25))
        height = float(data.get('height', 170.0))
        weight = float(data.get('weight', 70.0))
        program = data.get('program', 'Beginner (BG)')
        target_weight = float(data.get('target_weight', weight))

        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO clients (name, age, height, weight, program, target_weight)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, age, height, weight, program, target_weight))
                new_id = cur.lastrowid
                conn.commit()
            return jsonify({
                "id": new_id,
                "name": name,
                "age": age,
                "height": height,
                "weight": weight,
                "program": program,
                "target_weight": target_weight
            }), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Client with this name already exists"}), 409
    
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM clients").fetchall()
        clients = [dict(r) for r in rows]
    return jsonify(clients), 200

@app.route('/api/progress', methods=['GET', 'POST'])
def manage_progress():
    if request.method == 'POST':
        data = request.get_json() or {}
        client_id = data.get('client_id')
        week = data.get('week', 'Week 1')
        adherence = int(data.get('adherence', 85))
        current_weight = float(data.get('current_weight', 70.0))
        
        if not client_id:
            return jsonify({"error": "client_id is required"}), 400
        
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO progress (client_id, week, adherence, current_weight)
                VALUES (?, ?, ?, ?)
            """, (client_id, week, adherence, current_weight))
            conn.commit()
        return jsonify({"message": "Progress recorded successfully"}), 201

    with get_db() as conn:
        rows = conn.execute("""
            SELECT p.id, c.name as client_name, p.week, p.adherence, p.current_weight
            FROM progress p
            JOIN clients c ON p.client_id = c.id
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200

HTML_TEMPLATE_V2 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ACEest Functional Fitness v{{ version }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: #fff; margin: 0; padding: 0; }
        header { background: #d4af37; color: #000; padding: 20px; text-align: center; }
        h1 { margin: 0; font-size: 26px; }
        .version-badge { background: #000; color: #d4af37; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .card { background: #242424; border: 1px solid #333; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #d4af37; margin-top: 0; }
        .prog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }
        .prog-card { background: #2f2f2f; border-left: 4px solid #d4af37; padding: 15px; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #333; color: #d4af37; }
        .footer { text-align: center; color: #777; font-size: 13px; margin: 40px 0; }
    </style>
</head>
<body>
    <header>
        <h1>ACEest FUNCTIONAL FITNESS & GYM</h1>
        <span class="version-badge">v{{ version }} - SQLite Backed</span>
    </header>
    <div class="container">
        <div class="card">
            <h2>Active Training Programs</h2>
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
        <div class="card">
            <h2>Registered Clients (Database Records)</h2>
            <table>
                <tr>
                    <th>ID</th><th>Name</th><th>Age</th><th>Height</th><th>Weight</th><th>Program</th><th>Target Weight</th>
                </tr>
                {% for c in clients %}
                <tr>
                    <td>{{ c['id'] }}</td><td>{{ c['name'] }}</td><td>{{ c['age'] }}</td><td>{{ c['height'] }} cm</td><td>{{ c['weight'] }} kg</td><td>{{ c['program'] }}</td><td>{{ c['target_weight'] }} kg</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    <div class="footer">ACEest Fitness DevOps Assignment - v{{ version }}</div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
