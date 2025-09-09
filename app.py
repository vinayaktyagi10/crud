from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# MySQL connection (docker-compose provides env vars)
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "db"),
    user=os.getenv("MYSQL_USER", "user"),
    password=os.getenv("MYSQL_PASSWORD", "password"),
    database=os.getenv("MYSQL_DATABASE", "cruddb"),
    port=3306,
)
cursor = db.cursor(dictionary=True)

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255)
)
""")
db.commit()


# ------------------- ROUTES -------------------


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username, password = (
        data.get("username"),
        data.get("password"),
    )

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password),
        )
        db.commit()
        return jsonify({"message": "User registered"}), 201
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # handles duplicate entry as MySQL duplicate key.
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": "Database error"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s", (username, password)
    )
    user = cursor.fetchone()
    if user:
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/update_pass", methods=["POST"])
def update_pass():
    data = request.get_json()
    username, old_pass, new_pass = (
        data.get("username"),
        data.get("old_password"),
        data.get("new_password"),
    )

    if not username or not old_pass or not new_pass:
        return jsonify({"error": "Missing fields"}), 400

    # Verify old password
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s", (username, old_pass)
    )
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "Invalid username or old password"}), 401

    # Update password
    cursor.execute(
        "UPDATE users SET password=%s WHERE username=%s", (new_pass, username)
    )
    db.commit()
    return jsonify({"message": "Password updated"})


@app.route("/api/delete", methods=["POST"])
def delete_user():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Missing username"}), 400

    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted"})


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
