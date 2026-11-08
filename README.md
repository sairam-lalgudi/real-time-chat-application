# Real-Time Chat Application

A full-stack one-to-one chat application built with **Flask** and **MongoDB**. Users can register, log in, pick another user and exchange messages that are stored persistently. New messages appear automatically through short polling (every 2 seconds).

**Live demo:** _add your Render/Railway link here_

## Features

- User registration and login with hashed passwords (Werkzeug)
- Session-based authentication; protected pages and API endpoints
- One-to-one messaging between registered users
- Persistent message storage in MongoDB
- RESTful JSON API with input validation and proper HTTP status codes
- Near real-time updates using client-side polling with `fetch()`

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Database | MongoDB (PyMongo) |
| Frontend | HTML, CSS, JavaScript |
| Security | Werkzeug password hashing, Flask sessions |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/register` , POST `/register` | No | Show form / create a new user |
| GET | `/login` , POST `/login` | No | Show form / log in and start a session |
| GET | `/logout` | Yes | Clear the session |
| GET | `/chat` | Yes | Chat page with the list of other users |
| GET | `/api/messages/<user_id>` | Yes | Fetch the full conversation with a user, oldest first |
| POST | `/api/messages` | Yes | Send a message. Body: `{"receiver": "<user_id>", "text": "hello"}` |

**Status codes:** `200` OK, `400` invalid or missing input, `401` not logged in, `404` receiver not found.

## Database Design

- `users`: `username` (unique index), `password` (hash), `created_at`
- `messages`: `sender`, `receiver`, `text`, `created_at`
  - Compound index on `(sender, receiver, created_at)` for fast conversation lookups
  - A conversation is fetched with a MongoDB `$or` query (messages in both directions) sorted by `created_at`

## How to Run Locally

1. Install and start MongoDB (default: `mongodb://localhost:27017`)
2. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/sairam-lalgudi/real-time-chat-application.git
   cd real-time-chat-application
   pip install -r requirements.txt
   ```
3. (Optional) set environment variables:
   ```bash
   export SECRET_KEY="change-me"
   export MONGO_URI="mongodb://localhost:27017/"
   export FLASK_DEBUG=1   # development only
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000, register two accounts (use a second browser or a private window) and start chatting.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Signs session cookies | `dev-secret` (change in production) |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `FLASK_DEBUG` | Set to `1` to enable debug mode | off |

## Screenshots

_Add screenshots of the login page and the chat screen here._

## Future Improvements

- Replace polling with WebSockets (Flask-SocketIO) for true real-time delivery
- Message read receipts and unread counts
- Pagination for long conversations
- CSRF protection and rate limiting
