# Real-Time Chat Application
Resume stack: Flask, MongoDB, HTML, CSS, JavaScript.

Run:
1. Start MongoDB locally (mongodb://localhost:27017).
2. `pip install -r requirements.txt`
3. `python app.py`
4. Open http://127.0.0.1:5000
5. Register two accounts to test messaging.

Interview: Flask handles routes/API, MongoDB provides persistent users/messages, Werkzeug hashes passwords, JavaScript fetch() calls the APIs and polls every 2 seconds for new messages.
