from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)
from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

client = MongoClient(
    os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
)
db = client["chatapp"]
users = db["users"]
messages = db["messages"]

# Indexes: unique usernames, and fast lookup of a conversation sorted by time
users.create_index("username", unique=True)
messages.create_index(
    [("sender", ASCENDING), ("receiver", ASCENDING), ("created_at", ASCENDING)]
)

MAX_MESSAGE_LENGTH = 1000


def to_object_id(value):
    """Return an ObjectId, or None if the value is not a valid id."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


@app.route("/")
def index():
    return redirect(url_for("chat" if "user_id" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        elif users.find_one({"username": username}):
            error = "Username already exists."
        else:
            users.insert_one({
                "username": username,
                "password": generate_password_hash(password),
                "created_at": datetime.utcnow()
            })
            return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = users.find_one({
            "username": request.form.get("username", "").strip()
        })

        if user and check_password_hash(
            user["password"],
            request.form.get("password", "")
        ):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            return redirect(url_for("chat"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("login"))

    me = ObjectId(session["user_id"])

    user_list = list(
        users.find(
            {"_id": {"$ne": me}},
            {"password": 0}
        )
    )

    return render_template(
        "chat.html",
        username=session["username"],
        users=user_list
    )


@app.route("/api/messages/<user_id>")
def get_messages(user_id):
    if "user_id" not in session:
        return jsonify(error="Unauthorized"), 401

    other = to_object_id(user_id)
    if other is None:
        return jsonify(error="Invalid user id"), 400

    me = ObjectId(session["user_id"])

    cur = messages.find({
        "$or": [
            {"sender": me, "receiver": other},
            {"sender": other, "receiver": me}
        ]
    }).sort("created_at", 1)

    return jsonify([
        {
            "sender": str(m["sender"]),
            "text": m["text"],
            "time": m["created_at"].strftime("%H:%M")
        }
        for m in cur
    ])


@app.route("/api/messages", methods=["POST"])
def send_message():
    if "user_id" not in session:
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    receiver = to_object_id(data.get("receiver"))

    if not text or receiver is None:
        return jsonify(
            error="A message and a valid receiver are required"
        ), 400

    if len(text) > MAX_MESSAGE_LENGTH:
        return jsonify(
            error=f"Message must be under {MAX_MESSAGE_LENGTH} characters"
        ), 400

    if not users.find_one({"_id": receiver}, {"_id": 1}):
        return jsonify(error="Receiver not found"), 404

    messages.insert_one({
        "sender": ObjectId(session["user_id"]),
        "receiver": receiver,
        "text": text,
        "created_at": datetime.utcnow()
    })

    return jsonify(success=True)


if __name__ == "__main__":
    # Debug mode only when explicitly enabled (never in production)
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
