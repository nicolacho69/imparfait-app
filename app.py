from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import json
import datetime
import os

app = Flask(__name__)

# Load verbs/questions
with open("verbs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            total INTEGER,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, score, total, date FROM scores ORDER BY score DESC, date DESC LIMIT 5")
    top_scores = c.fetchall()
    conn.close()
    return render_template("index.html", top_scores=top_scores)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        username = request.form.get("username", "Étudiant")
    else:
        username = "Étudiant"
    # choose 5 random questions
    questions = random.sample(data["questions"], min(5, len(data["questions"])))
    return render_template("quiz.html", questions=questions, username=username)

@app.route("/result", methods=["POST"])
def result():
    username = request.form.get("username", "Étudiant")
    # q_ids are sent as repeated hidden inputs
    q_ids = request.form.getlist("q_ids")
    score = 0
    total = len(q_ids)
    # Build a lookup for answers
    answer_lookup = {q["id"]: q["answer"] for q in data["questions"]}
    for qid in q_ids:
        user_ans = request.form.get(qid, "")
        correct = answer_lookup.get(qid, "")
        if user_ans and user_ans.strip().lower() == correct.strip().lower():
            score += 1

    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO scores (username, score, total, date) VALUES (?, ?, ?, ?)",
        (username, score, total, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

    return render_template("result.html", username=username, score=score, total=total)

if __name__ == "__main__":
    # For Render compatibility: listen on 0.0.0.0 and use PORT env if provided
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
