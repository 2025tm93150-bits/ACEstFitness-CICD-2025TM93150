import json
import pytest

def test_health_check(client):
    """Verify Kubernetes liveness probe returns HTTP 200 with healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'ACEest-Fitness'
    assert 'version' in data
    assert 'timestamp' in data

def test_readiness_probe(client):
    """Verify Kubernetes readiness probe returns HTTP 200 with database connectivity."""
    response = client.get('/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ready'] is True
    assert data['database'] == 'connected'

def test_version_endpoint(client):
    """Verify version endpoint reports correct application metadata."""
    response = client.get('/version')
    assert response.status_code == 200
    data = response.get_json()
    assert 'version' in data
    assert 'environment' in data

def test_metrics_endpoint(client):
    """Verify metrics endpoint exposes operational counters."""
    response = client.get('/metrics')
    assert response.status_code == 200
    data = response.get_json()
    assert data['app_name'] == 'aceest_fitness'
    assert 'uptime_seconds' in data
    assert 'active_clients' in data
    assert data['active_clients'] >= 1

def test_home_page(client):
    """Verify web dashboard loads successfully and renders brand components."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"ACEest FUNCTIONAL FITNESS" in response.data
    assert b"Fat Loss (FL)" in response.data
    assert b"Muscle Gain (MG)" in response.data

def test_get_programs_api(client):
    """Verify /api/programs returns structured workout and diet specifications."""
    response = client.get('/api/programs')
    assert response.status_code == 200
    data = response.get_json()
    assert "Fat Loss (FL)" in data
    assert "Muscle Gain (MG)" in data
    assert "Beginner (BG)" in data
    assert data["Fat Loss (FL)"]["target_calories"] == 2000

def test_calculate_bmi_valid(client):
    """Verify BMI calculator calculates correct value and clinical category."""
    payload = {"weight": 70.0, "height": 175.0}
    response = client.post('/api/calculate-bmi',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['bmi'] == 22.86
    assert data['category'] == "Normal weight"

def test_calculate_bmi_underweight(client):
    """Verify BMI calculation for underweight category."""
    payload = {"weight": 45.0, "height": 170.0}
    response = client.post('/api/calculate-bmi',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['category'] == "Underweight"

def test_calculate_bmi_invalid(client):
    """Verify BMI calculator returns HTTP 400 on zero or negative values."""
    payload = {"weight": -10, "height": 170.0}
    response = client.post('/api/calculate-bmi',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_client_registration_and_retrieval(client):
    """Verify registering a new client and fetching existing clients."""
    new_client = {
        "name": "Arjun Kapoor",
        "age": 29,
        "height": 180.0,
        "weight": 82.0,
        "target_weight": 76.0,
        "program": "Fat Loss (FL)"
    }
    response = client.post('/api/clients',
                           data=json.dumps(new_client),
                           content_type='application/json')
    assert response.status_code == 201
    created = response.get_json()
    assert created['name'] == "Arjun Kapoor"
    assert created['bmi'] == 25.31
    assert created['bmi_category'] == "Overweight"

    # Fetch list
    get_res = client.get('/api/clients')
    assert get_res.status_code == 200
    clients_list = get_res.get_json()
    names = [c['name'] for c in clients_list]
    assert "Arjun Kapoor" in names

def test_client_registration_duplicate(client):
    """Verify duplicate client name returns HTTP 409 conflict."""
    client_data = {
        "name": "Unique Name Test",
        "age": 30,
        "height": 175.0,
        "weight": 70.0,
        "program": "Beginner (BG)"
    }
    res1 = client.post('/api/clients', data=json.dumps(client_data), content_type='application/json')
    assert res1.status_code == 201

    res2 = client.post('/api/clients', data=json.dumps(client_data), content_type='application/json')
    assert res2.status_code == 409

def test_client_registration_missing_name(client):
    """Verify validation error when client name is omitted."""
    client_data = {"age": 25, "weight": 65.0}
    res = client.post('/api/clients', data=json.dumps(client_data), content_type='application/json')
    assert res.status_code == 400

def test_get_single_client(client):
    """Verify single client lookup by primary key."""
    res = client.get('/api/clients/1')
    assert res.status_code == 200
    data = res.get_json()
    assert 'name' in data

    # Non-existent ID
    res_404 = client.get('/api/clients/99999')
    assert res_404.status_code == 404

def test_log_workout(client):
    """Verify workout logging API."""
    workout_data = {
        "client_name": "Vikram Seth",
        "workout_type": "Kettlebell Cleans & Sprints",
        "duration_min": 40,
        "calories_burned": 380,
        "date": "2026-11-22"
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 201
    created = response.get_json()
    assert created['client_name'] == "Vikram Seth"
    assert created['calories_burned'] == 380

    # Get workouts
    res_list = client.get('/api/workouts')
    assert res_list.status_code == 200
    assert len(res_list.get_json()) >= 1

def test_log_workout_missing_fields(client):
    """Verify validation when workout fields are missing."""
    response = client.post('/api/workouts', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400

def test_web_register_client_flow(client):
    """Verify HTML form submission for client registration."""
    form_data = {
        "name": "Deepika Padukone",
        "age": "32",
        "height": "174",
        "weight": "57",
        "target_weight": "58",
        "program": "Beginner (BG)"
    }
    response = client.post('/web/register-client', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Deepika Padukone" in response.data
