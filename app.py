import os
from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# 读取环境变量（Render 上也会生效）
load_dotenv()

# 发送端鉴权用的 token：到 Render -> Settings -> Environment Variables 设置 SENDER_TOKEN
SENDER_TOKEN = os.getenv("SENDER_TOKEN", "changeme")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "dev-secret")

# 关键：明确使用 eventlet；并允许跨域，方便手机/平板访问
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

# 保存“最近一条消息”（供新连接的屏幕端立即显示）
last_message = {"text": "你好外公 🌞"}

@app.route("/")
def index():
    # 主页简单提示
    return "OK. Use /send?t=YOUR_TOKEN (phone) and /screen (iPad)."

@app.route("/send")
def send_page():
    # 发送端页需要在 URL 带 ?t=TOKEN
    token = request.args.get("t", "")
    if token != SENDER_TOKEN:
        return abort(403, "Forbidden: invalid token.")
    return render_template("send.html")

@app.route("/screen")
def screen_page():
    # 显示端不要求 token（你也可以自己改成要求）
    return render_template("screen.html")

# ---------- Socket.IO：发送端 ----------
@socketio.on("connect", namespace="/send")
def send_connect():
    emit("status", {"ok": True, "msg": "已连接"}, namespace="/send")

@socketio.on("push", namespace="/send")
def handle_push(data):
    token = (data or {}).get("token", "")
    text = ((data or {}).get("text") or "").strip()

    if token != SENDER_TOKEN:
        emit("result", {"ok": False, "msg": "Invalid token"}, namespace="/send")
        return

    if not text:
        emit("result", {"ok": False, "msg": "内容不能为空"}, namespace="/send")
        return

    # 更新内存里的“最近一条”并广播给所有屏幕端
    global last_message
    last_message = {"text": text}
    socketio.emit("update", last_message, namespace="/screen")
    emit("result", {"ok": True, "msg": "已发送"}, namespace="/send")

# ---------- Socket.IO：显示端 ----------
@socketio.on("connect", namespace="/screen")
def screen_connect():
    # 新连接的显示端，立刻收到最新一条
    emit("update", last_message, namespace="/screen")

if __name__ == "__main__":
    # 本地调试用；Render 上由 gunicorn 启动
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
