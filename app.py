from flask import Flask, request, jsonify, redirect
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime, timedelta

from config import BASE_URL, JWT_SECRET_KEY, JWT_EXPIRES_HOURS
from models import (
    create_url, get_url, increment_clicks,
    create_user, get_user_by_email, get_urls_by_user
)
from utils import generate_short_id
from auth_utils import hash_password, check_password

app = Flask(__name__)

# JWT Config
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=JWT_EXPIRES_HOURS)

jwt = JWTManager(app)


# ================= AUTH =================

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email & password required"}), 400

    hashed_pw = hash_password(password)

    result = create_user({
        "email": email,
        "password": hashed_pw
    })

    if not result:
        return jsonify({"error": "User already exists"}), 400

    return jsonify({"message": "User created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = get_user_by_email(email)

    if not user or not check_password(password, user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=email)

    return jsonify({"access_token": token}), 200


# ================= URL =================

@app.route("/shorten", methods=["POST"])
@jwt_required()
def shorten_url():
    current_user = get_jwt_identity()

    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL required"}), 400

    short_id = generate_short_id()

    url_data = {
        "original_url": original_url,
        "short_id": short_id,
        "user": current_user,
        "created_at": datetime.utcnow(),
        "clicks": 0
    }

    result = create_url(url_data)

    if not result:
        return jsonify({"error": "Failed to create URL"}), 500

    return jsonify({
        "short_url": f"{BASE_URL}/{short_id}"
    }), 201


@app.route("/<short_id>", methods=["GET"])
def redirect_url(short_id):
    url = get_url(short_id)

    if not url:
        return jsonify({"error": "URL not found"}), 404

    increment_clicks(short_id)

    return redirect(url["original_url"])


@app.route("/stats/<short_id>", methods=["GET"])
@jwt_required()
def get_stats(short_id):
    current_user = get_jwt_identity()

    url = get_url(short_id)

    if not url:
        return jsonify({"error": "Not found"}), 404

    if url["user"] != current_user:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({
        "original_url": url["original_url"],
        "clicks": url["clicks"],
        "created_at": url["created_at"]
    })


@app.route("/myurls", methods=["GET"])
@jwt_required()
def my_urls():
    current_user = get_jwt_identity()

    urls = get_urls_by_user(current_user)

    result = []
    for u in urls:
        result.append({
            "short_url": f"{BASE_URL}/{u['short_id']}",
            "original_url": u["original_url"],
            "clicks": u["clicks"]
        })

    return jsonify(result)


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)