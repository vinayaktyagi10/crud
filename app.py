from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["cruddb"]
users_collection = db["users"]


@app.route("/api/register", methods=["POST"])
def add_user():
    try:
        data = request.get_json()
        if not data or "id" not in data or "password" not in data:
            return jsonify({"error": "Missing 'id' or 'password'"}), 400
        user_id = data["id"]
        password = data["password"]
        if users_collection.find_one({"id": user_id}):
            return jsonify({"error": "User already exists"}), 409

        users_collection.insert_one({"id": user_id, "password": password})

        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["GET", "POST"])
def login():
    data = request.get_json()
    if not data or "id" not in data or "password" not in data:
        return jsonify({"error": "Missing 'id' or 'password'"}), 400
    user_id = data["id"]
    password = data["password"]
    user = users_collection.find_one({"id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user["password"] != password:
        return jsonify({"error": "Incorrect password"}), 401
    return jsonify({"message": "User logged in"}), 200


@app.route("/api/update", methods=["POST"])
def update_pass():
    data = request.get_json()
    if (
        not data
        or "id" not in data
        or "old_password" not in data
        or "new_password" not in data
    ):
        return jsonify({"error": "Missing 'id', 'old_password' or 'new_password"}), 400
    user_id = data["id"]
    old_password = data["old_password"]
    new_password = data["new_password"]
    user = users_collection.find_one({"id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user["password"] != old_password:
        return jsonify({"error": "Incorrect old password"}), 401
    users_collection.update_one({"id": user_id}, {"$set": {"password": new_password}})
    return jsonify({"message": "Password updated successfully"}), 200


@app.route("/api/delete", methods=["POST"])
def delete_user():
    data = request.get_json()
    if not data or "id" not in data or "password" not in data:
        return jsonify({"error": "Missing 'id' or 'password'"}), 400
    user_id = data["id"]
    password = data["password"]
    user = users_collection.find_one({"id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user["password"] != password:
        return jsonify({"error": "Incorrect password"}), 401
    users_collection.delete_one({"id": user_id})
    return jsonify({"message": "User deleted"}), 200


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
