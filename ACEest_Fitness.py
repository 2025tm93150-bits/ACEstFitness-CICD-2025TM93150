"""
ACEest Fitness & Gym Management System - Version 3.0.0
Flagship Production Release for CI/CD Automated DevOps Pipeline.
Incorporates role-based fitness management, workout logging, SQLite persistence,
system metrics, and Kubernetes health/readiness probe endpoints.
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
import os
import time
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'aceest-production-key-v3')

VERSION = os.environ.get("APP_VERSION", "3.0.0")
DB_NAME = os.environ.get("DB_NAME", "aceest_fitness.db")
ENVIRONMENT = os.environ.get("DEPLOY_ENV", "production")
DEPLOYMENT_COLOR = os.environ.get("DEPLOYMENT_COLOR", "green") # blue or green
POD_NAME = os.environ.get("HOSTNAME", "local-node")

START_TIME = time.time()
REQUEST_COUNTER = 0

# Program definitions with workout and diet specifications
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
    },
    "HIIT Performance (HP)": {
        "id": "HP",
        "name": "HIIT Performance (HP) [v3 Feature]",
        "workout": "Mon: 45min Tabata Sprints | Tue: Kettlebell Complex | Wed: Olympic Lifting Skills | Thu: 5km Ruck Run | Fri: Recovery Yoga",
        "diet": "High Protein Low Carb: Whey + Almonds | Lunch: Grilled Paneer/Tofu Quinoa | Dinner: Lentil Soup + Greens | Target: 2,400 kcal",
        "target_calories": 2400,
        "color": "#f39c12"
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
                age INTEGER NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                program TEXT NOT NULL,
                target_weight REAL NOT NULL,
                membership_status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                adherence INTEGER NOT NULL,
                current_weight REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                duration_min INTEGER NOT NULL,
                calories_burned INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)
        
        # Seed initial dataset if table empty
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clients")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, program, target_weight, membership_status)
                VALUES ('Vikram Seth', 30, 178.0, 84.0, 'Fat Loss (FL)', 75.0, 'Active')
            """)
            c1 = cur.lastrowid
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, program, target_weight, membership_status)
                VALUES ('Ananya Roy', 26, 165.0, 58.0, 'Muscle Gain (MG)', 62.0, 'Active')
            """)
            c2 = cur.lastrowid
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, program, target_weight, membership_status)
                VALUES ('Karthik Raman', 34, 172.0, 88.0, 'HIIT Performance (HP) [v3 Feature]', 78.0, 'Active')
            """)
            
            cur.execute("""
                INSERT INTO progress (client_id, week, adherence, current_weight, notes)
                VALUES (?, 'Week 1', 92, 83.1, 'Consistent diet compliance')
            """, (c1,))
            cur.execute("""
                INSERT INTO progress (client_id, week, adherence, current_weight, notes)
                VALUES (?, 'Week 1', 88, 58.6, 'Hit compound lifting targets')
            """, (c2,))
            
            cur.execute("""
                INSERT INTO workouts (client_name, workout_type, duration_min, calories_burned, date)
                VALUES ('Vikram Seth', 'Assault Bike + AMRAP', 45, 480, '2026-11-20')
            """)
            cur.execute("""
                INSERT INTO workouts (client_name, workout_type, duration_min, calories_burned, date)
                VALUES ('Ananya Roy', 'Squat & Bench Press 5x5', 60, 420, '2026-11-21')
            """)
            conn.commit()

init_db()

@app.before_request
def count_requests():
    global REQUEST_COUNTER
    REQUEST_COUNTER += 1

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100.0
    if height_m <= 0:
        return 0.0, "Invalid height"
    bmi = round(weight_kg / (height_m * height_m), 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category

# ==================== WEB DASHBOARD ====================
HTML_DASHBOARD_V3 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACEest Functional Fitness & Gym - v{{ version }}</title>
    <style>
        :root {
            --primary: #d4af37;
            --primary-dark: #b8972e;
            --bg-dark: #121212;
            --card-bg: #1e1e1e;
            --card-border: #333333;
            --text-light: #f5f5f5;
            --text-muted: #a0a0a0;
            --accent-green: #2ecc71;
            --accent-red: #e74c3c;
            --accent-blue: #3498db;
        }
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        header {
            background: linear-gradient(135deg, #1f1c18 0%, #0d0d0d 100%);
            border-bottom: 3px solid var(--primary);
            padding: 24px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header-title h1 {
            margin: 0;
            font-size: 26px;
            letter-spacing: 1.5px;
            color: var(--primary);
            text-transform: uppercase;
        }
        .header-title p {
            margin: 4px 0 0 0;
            font-size: 13px;
            color: var(--text-muted);
        }
        .header-badges {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-version { background: var(--primary); color: #000; }
        .badge-env { background: #333; color: #fff; border: 1px solid #555; }
        .badge-status { background: #1b4d2e; color: #4ade80; }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            border-top: 3px solid var(--primary);
        }
        .stat-label { font-size: 13px; color: var(--text-muted); text-transform: uppercase; }
        .stat-value { font-size: 28px; font-weight: bold; color: #fff; margin-top: 6px; }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 25px;
        }
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .card h2 {
            margin-top: 0;
            font-size: 18px;
            color: var(--primary);
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }
        .prog-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        @media (max-width: 600px) {
            .prog-grid { grid-template-columns: 1fr; }
        }
        .prog-box {
            background: #252525;
            border-left: 4px solid var(--primary);
            padding: 15px;
            border-radius: 6px;
        }
        .prog-box h4 { margin: 0 0 8px 0; font-size: 15px; }
        .prog-box p { margin: 4px 0; font-size: 12px; color: #ccc; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        th, td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #2a2a2a;
        }
        th { background: #262626; color: var(--primary); font-weight: 600; }
        tr:hover { background: #282828; }

        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        .form-control {
            width: 100%;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #444;
            background: #282828;
            color: #fff;
            box-sizing: border-box;
            font-size: 14px;
        }
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
        }
        .btn {
            background: var(--primary);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: 0.2s;
        }
        .btn:hover { background: var(--primary-dark); }
        .footer {
            text-align: center;
            color: #666;
            font-size: 12px;
            padding: 30px;
            border-top: 1px solid #222;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <h1>ACEest FUNCTIONAL FITNESS & GYM</h1>
            <p>Automated Enterprise CI/CD Cloud Platform &bull; Pod: {{ pod_name }}</p>
        </div>
        <div class="header-badges">
            <span class="badge badge-version">v{{ version }}</span>
            <span class="badge badge-env">{{ environment }}</span>
            <span class="badge badge-status">&bull; Operational</span>
        </div>
    </header>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Active Clients</div>
                <div class="stat-value">{{ client_count }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Workouts Logged</div>
                <div class="stat-value">{{ workout_count }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Adherence</div>
                <div class="stat-value">{{ avg_adherence }}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">System Uptime</div>
                <div class="stat-value">{{ uptime_sec }}s</div>
            </div>
        </div>

        <div class="main-grid">
            <div>
                <div class="card">
                    <h2>Training Programs & Nutrition Matrix</h2>
                    <div class="prog-grid">
                        {% for key, prog in programs.items() %}
                        <div class="prog-box" style="border-left-color: {{ prog.color }};">
                            <h4 style="color: {{ prog.color }};">{{ prog.name }}</h4>
                            <p><strong>Workout:</strong> {{ prog.workout }}</p>
                            <p><strong>Diet:</strong> {{ prog.diet }}</p>
                            <p><strong>Target:</strong> {{ prog.target_calories }} kcal</p>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="card">
                    <h2>Enrolled Gym Members</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Age</th>
                                <th>Height</th>
                                <th>Weight</th>
                                <th>Target</th>
                                <th>Program</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in clients %}
                            <tr>
                                <td><strong>{{ c['name'] }}</strong></td>
                                <td>{{ c['age'] }}</td>
                                <td>{{ c['height'] }} cm</td>
                                <td>{{ c['weight'] }} kg</td>
                                <td>{{ c['target_weight'] }} kg</td>
                                <td>{{ c['program'] }}</td>
                                <td><span style="color: #4ade80;">{{ c['membership_status'] }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="card">
                    <h2>Recent Workout Sessions</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Member</th>
                                <th>Workout Routine</th>
                                <th>Duration</th>
                                <th>Calories</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for w in workouts %}
                            <tr>
                                <td>{{ w['client_name'] }}</td>
                                <td>{{ w['workout_type'] }}</td>
                                <td>{{ w['duration_min'] }} min</td>
                                <td>{{ w['calories_burned'] }} kcal</td>
                                <td>{{ w['date'] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div>
                <div class="card">
                    <h2>Register New Client</h2>
                    <form method="POST" action="/web/register-client">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" name="name" class="form-control" placeholder="e.g. Rohan Mehta" required>
                        </div>
                        <div class="form-group">
                            <label>Age</label>
                            <input type="number" name="age" class="form-control" value="28" required>
                        </div>
                        <div class="form-group">
                            <label>Height (cm)</label>
                            <input type="number" step="0.1" name="height" class="form-control" value="175" required>
                        </div>
                        <div class="form-group">
                            <label>Weight (kg)</label>
                            <input type="number" step="0.1" name="weight" class="form-control" value="78" required>
                        </div>
                        <div class="form-group">
                            <label>Target Weight (kg)</label>
                            <input type="number" step="0.1" name="target_weight" class="form-control" value="72" required>
                        </div>
                        <div class="form-group">
                            <label>Fitness Program</label>
                            <select name="program" class="form-control">
                                {% for key, prog in programs.items() %}
                                <option value="{{ key }}">{{ prog.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="btn">Register Client</button>
                    </form>
                </div>

                <div class="card">
                    <h2>DevOps Cluster Info</h2>
                    <p style="font-size: 13px; color: #aaa;">
                        <strong>App Version:</strong> {{ version }}<br>
                        <strong>Environment:</strong> {{ environment }}<br>
                        <strong>Deployment Color:</strong> {{ deployment_color }}<br>
                        <strong>Active Pod Hostname:</strong> {{ pod_name }}<br>
                        <strong>Total Handled Requests:</strong> {{ request_count }}
                    </p>
                    <div style="margin-top: 15px; font-size: 12px; border-top: 1px solid #333; padding-top: 10px;">
                        <a href="/health" target="_blank" style="color: var(--primary); text-decoration: none;">&rarr; Liveness Probe (/health)</a><br>
                        <a href="/ready" target="_blank" style="color: var(--primary); text-decoration: none;">&rarr; Readiness Probe (/ready)</a><br>
                        <a href="/metrics" target="_blank" style="color: var(--primary); text-decoration: none;">&rarr; Metrics Endpoint (/metrics)</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        ACEest Functional Fitness DevOps CI/CD Implementation &bull; BITS Pilani Assignment 2 &bull; Version {{ version }}
    </div>
</body>
</html>
"""

# ==================== CONTROLLER ROUTES ====================

@app.route('/')
def home():
    with get_db() as conn:
        clients = conn.execute("SELECT * FROM clients ORDER BY id DESC").fetchall()
        workouts = conn.execute("SELECT * FROM workouts ORDER BY id DESC LIMIT 5").fetchall()
        adherence_row = conn.execute("SELECT AVG(adherence) FROM progress").fetchone()
        avg_adherence = round(adherence_row[0], 1) if adherence_row and adherence_row[0] else 90.0

    uptime_sec = int(time.time() - START_TIME)

    return render_template_string(
        HTML_DASHBOARD_V3,
        programs=PROGRAMS,
        clients=clients,
        workouts=workouts,
        client_count=len(clients),
        workout_count=len(workouts),
        avg_adherence=avg_adherence,
        uptime_sec=uptime_sec,
        version=VERSION,
        environment=ENVIRONMENT,
        deployment_color=DEPLOYMENT_COLOR,
        pod_name=POD_NAME,
        request_count=REQUEST_COUNTER
    )

@app.route('/web/register-client', methods=['POST'])
def web_register_client():
    name = request.form.get('name', '').strip()
    age = int(request.form.get('age', 25))
    height = float(request.form.get('height', 170.0))
    weight = float(request.form.get('weight', 70.0))
    target_weight = float(request.form.get('target_weight', weight))
    program = request.form.get('program', 'Beginner (BG)')

    if name:
        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO clients (name, age, height, weight, program, target_weight)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, age, height, weight, program, target_weight))
                conn.commit()
        except sqlite3.IntegrityError:
            pass  # Name already exists
    return home()

# ==================== K8S PROBES & DEVOPS ENDPOINTS ====================

@app.route('/health')
def health():
    """Liveness probe for Kubernetes."""
    return jsonify({
        "status": "healthy",
        "service": "ACEest-Fitness",
        "version": VERSION,
        "environment": ENVIRONMENT,
        "pod": POD_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/ready')
def ready():
    """Readiness probe for Kubernetes ensuring DB connection."""
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
def get_version():
    """Endpoint used by CI/CD and deployment strategy verifications."""
    return jsonify({
        "version": VERSION,
        "deployment_color": DEPLOYMENT_COLOR,
        "environment": ENVIRONMENT,
        "pod": POD_NAME
    }), 200

@app.route('/metrics')
def metrics():
    """Prometheus / monitoring metrics endpoint."""
    with get_db() as conn:
        client_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        workout_count = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]

    return jsonify({
        "app_name": "aceest_fitness",
        "version": VERSION,
        "uptime_seconds": int(time.time() - START_TIME),
        "total_requests": REQUEST_COUNTER,
        "active_clients": client_count,
        "total_workouts": workout_count
    }), 200

# ==================== REST APIS ====================

@app.route('/api/programs', methods=['GET'])
def get_programs():
    # Support A/B test flag via header or query param
    ab_treatment = request.headers.get('X-Experiment-Group') == 'treatment' or request.args.get('variant') == 'b'
    programs_payload = dict(PROGRAMS)
    if not ab_treatment:
        # In baseline A version, hide experimental HP program if requested
        pass
    return jsonify(programs_payload), 200

@app.route('/api/clients', methods=['GET', 'POST'])
def api_clients():
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({"error": "Name is required"}), 400

        age = int(data.get('age', 25))
        height = float(data.get('height', 170.0))
        weight = float(data.get('weight', 70.0))
        target_weight = float(data.get('target_weight', weight))
        program = data.get('program', 'Beginner (BG)')

        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO clients (name, age, height, weight, program, target_weight)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, age, height, weight, program, target_weight))
                new_id = cur.lastrowid
                conn.commit()

            bmi, category = calculate_bmi(weight, height)
            return jsonify({
                "id": new_id,
                "name": name,
                "age": age,
                "height": height,
                "weight": weight,
                "target_weight": target_weight,
                "program": program,
                "bmi": bmi,
                "bmi_category": category
            }), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Client with this name already exists"}), 409

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM clients ORDER BY id ASC").fetchall()
        return jsonify([dict(r) for r in rows]), 200

@app.route('/api/clients/<int:client_id>', methods=['GET'])
def api_get_client(client_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        if not row:
            return jsonify({"error": "Client not found"}), 404
        return jsonify(dict(row)), 200

@app.route('/api/calculate-bmi', methods=['POST'])
def api_bmi():
    data = request.get_json() or {}
    try:
        weight = float(data.get('weight', 0))
        height = float(data.get('height', 0))
        if weight <= 0 or height <= 0:
            return jsonify({"error": "Weight and height must be positive numbers"}), 400

        bmi, category = calculate_bmi(weight, height)
        return jsonify({
            "weight_kg": weight,
            "height_cm": height,
            "bmi": bmi,
            "category": category
        }), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input parameters: {str(e)}"}), 400

@app.route('/api/workouts', methods=['GET', 'POST'])
def api_workouts():
    if request.method == 'POST':
        data = request.get_json() or {}
        client_name = data.get('client_name', '').strip()
        workout_type = data.get('workout_type', '').strip()
        duration_min = int(data.get('duration_min', 30))
        calories_burned = int(data.get('calories_burned', 200))
        date_str = data.get('date', datetime.now().strftime("%Y-%m-%d"))

        if not client_name or not workout_type:
            return jsonify({"error": "client_name and workout_type are required"}), 400

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO workouts (client_name, workout_type, duration_min, calories_burned, date)
                VALUES (?, ?, ?, ?, ?)
            """, (client_name, workout_type, duration_min, calories_burned, date_str))
            new_id = cur.lastrowid
            conn.commit()

        return jsonify({
            "id": new_id,
            "client_name": client_name,
            "workout_type": workout_type,
            "duration_min": duration_min,
            "calories_burned": calories_burned,
            "date": date_str
        }), 201

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM workouts ORDER BY id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
