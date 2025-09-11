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
            return jsonify({"error": "User exists"}), 409

        users_collection.insert_one({"id": user_id, "password": password})

        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
