"""CampusFix 校园报修工单系统 - Flask 入口"""
import logging
import os
import sqlite3
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

# 项目根目录（本文件所在目录）
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE = Path(os.environ.get("DATABASE_PATH", INSTANCE_DIR / "campusfix.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret")

# 基本日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("campusfix")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/")
def index():
    db = get_db()
    tickets = db.execute(
        "SELECT id, title, room, status, created_at FROM tickets ORDER BY created_at DESC"
    ).fetchall()
    return render_template("index.html", tickets=tickets)

@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):
    db = get_db()
    ticket = db.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()
    if ticket is None:
        return render_template("404.html"), 404
    return render_template("detail.html", ticket=ticket)

# 这是你课14写的函数，保留在这里
def validate_ticket(title, room):
    if len(title) > 20:
        return "标题不能超过20个字符"
    return None

# 这是唯一的 create_ticket 路由
@app.route("/tickets/new", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        room = request.form.get("room", "").strip()
        description = request.form.get("description", "").strip()

        # 校验逻辑
        error = validate_ticket(title, room)
        if error:
            return error, 400

        db = get_db()
        db.execute(
            "INSERT INTO tickets (title, room, description) VALUES (?, ?, ?)",
            (title, room, description),
        )
        db.commit()
        logger.info("created ticket: %s (%s)", title, room)
        return redirect(url_for("index"))
    return render_template("new.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)