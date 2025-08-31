from gevent import monkey
monkey.patch_all()  # 必须：在导入 Flask/SocketIO 之前 monkey-patch

import os
from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

load_dotenv()

SENDER_TOKEN = os.getenv("SENDER_TOKEN", "change_me_please")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "a-very-secret-key")

# 明确使用 gevent；顺便设置心跳，跨域放开
socketio = SocketIO(
    app,
    async_mode="gevent",
    cors_allowed_origins="*",
    ping_interval=10,
    ping_timeout=20,
)

last_message = {"text": "你好外公 🌞", "ts": None}

@app.route("/")
def index():
    return 'OK. Use /send (phone) and /screen (iPad).'

@app.route("/send")
def send_page():
    token = request.args.get("t", "")
    if token != SENDER_TOKEN:
        return abort(403, "Forbidden: invalid token.")
    return render_template("send.html")

@app.route("/screen")
def screen_page():
    return render_template("screen.html")

# —— 连接事件：给出状态提示，便于你在页面看到“已连接” —— #
@socketio.on("connect", namespace="/send")
def on_send_connect():
    emit("result", {"ok": True, "msg": "已连接"}, namespace="/send")

@socketio.on("connect", namespace="/screen")
def on_screen_connect():
    emit("update", last_message, namespace="/screen")

@socketio.on("push", namespace="/send")
def handle_push(data):
    token = data.get("token", "")
    text = (data.get("text") or "").strip()
    if token != SENDER_TOKEN:
        emit("result", {"ok": False, "msg": "Invalid token"}, namespace="/send")
        return
    if not text:
        emit("result", {"ok": False, "msg": "内容不能为空"}, namespace="/send")
        return

    global last_message
    last_message = {"text": text}
    socketio.emit("update", last_message, namespace="/screen")
    emit("result", {"ok": True, "msg": "已发送"}, namespace="/send")

if __name__ == "__main__":
    # 本地调试用；Render 上由 gunicorn 启动
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    # 生产可换为 socketio.run(app, host="0.0.0.0", port=8000, debug=False)
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
