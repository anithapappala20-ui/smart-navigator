from flask import Flask, render_template, request, jsonify, redirect
import requests
import sqlite3
from datetime import datetime


conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE travel_records ADD COLUMN vehicle TEXT")
    print("✅ vehicle column added")
except:
    print("⚠️ vehicle column already exists")

try:
    cursor.execute("ALTER TABLE travel_records ADD COLUMN cost REAL")
    print("✅ cost column added")
except:
    print("⚠️ cost column already exists")

conn.commit()
conn.close()

app = Flask(__name__)

# ==============================
# CONFIGURATION
# ==============================

WEATHER_API_KEY = "78a099a6d47bb5aa350510498003f1c2"   # <-- Put your API key here

# ==============================
# DATABASE SETUP
# ==============================

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS travel_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        start_location TEXT,
        destination TEXT,
        distance REAL,
        vehicle TEXT,
        cost REAL,
        travel_date TEXT
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():
    return redirect("/login")
@app.route("/home")
def home_page():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


# ==============================
# WEATHER API
# ==============================

@app.route("/weather", methods=["POST"])
def weather():
    data = request.json
    lat = data["lat"]
    lon = data["lon"]

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if "main" not in response:
        return jsonify({"error": "Weather data not found"})

    return jsonify({
        "temp": response["main"]["temp"],
        "desc": response["weather"][0]["description"]
    })


# ==============================
# SAVE TRAVEL RECORD
# ==============================

@app.route("/save_travel", methods=["POST"])
def save_travel():
    data = request.json
    
    username = data["username"]
    start = data["start"]
    destination = data["destination"]
    distance = data["distance"]
    vehicle = data["vehicle"]
    cost = data["cost"]
    travel_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO travel_records 
    (username, start_location, destination, distance,vehicle,cost, travel_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, start, destination, distance,vehicle,cost, travel_date))

    conn.commit()
    conn.close()

    return jsonify({"message": "Travel record saved successfully"})


# ==============================
# VIEW ALL TRAVEL RECORDS
# ==============================

@app.route("/get_travels/<username>")
def get_travels(username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT start_location, destination, distance,vehicle,cost, travel_date 
    FROM travel_records 
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    records = cursor.fetchall()
    conn.close()

    result = []
    for r in records:
        result.append({
            "start": r[0],
            "end": r[1],
            "distance": r[2],
            "vehicle": r[3],
            "cost": r[4],
            "date": r[5]
        })

    return jsonify(result)

@app.route("/clear_travels/<username>", methods=["POST"])
def clear_travels(username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM travel_records WHERE username=?", (username,))

    conn.commit()
    conn.close()

    return jsonify({"message": "History cleared"})

# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    print("🚀 Smart Navigation Server Running...")
    app.run(host="127.0.0.1", port=5000, debug=True)