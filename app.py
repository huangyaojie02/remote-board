import os
from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

load_dotenv()

# 简单安全：发送端需要携带TOKEN
SENDER_TOKEN = os.getenv("SENDER_TOKEN", "change_me_please")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "a-very-secret-key")
socketio = SocketIO(app, cors_allowed_origins="*")  # 局域网/公网都可

# 内存里保存“最近一条消息”，断线重连也能显示
last_message = {
    "text": "你好外公 🌞",
    "ts": None
}

@app.route("/")
def index():
    return 'OK. Use /send (phone) and /screen (iPad).'

@app.route("/send")
def send_page():
    # 访问发送页也要带 token ?t=XXXX
    token = request.args.get("t", "")
    if token != SENDER_TOKEN:
        return abort(403, "Forbidden: invalid token.")
    return render_template("send.html")

@app.route("/screen")
def screen_page():
    # 屏幕端不要求 token（也可改成要求）
    return render_template("screen.html")

@socketio.on("connect", namespace="/screen")
def screen_connect():
    # 新的显示端连上来，给它推送最近一条消息
    emit("update", last_message, namespace="/screen")

@socketio.on("push", namespace="/send")
def handle_push(data):
    # 发送端推送消息：检查token、防注入
    token = data.get("token", "")
    text = (data.get("text") or "").strip()
    if token != SENDER_TOKEN:
        emit("result", {"ok": False, "msg": "Invalid token"}, namespace="/send")
        return
    if not text:
        emit("result", {"ok": False, "msg": "内容不能为空"}, namespace="/send")
        return

    # 更新最近消息并广播给所有屏幕
    global last_message
    last_message = {"text": text}
    socketio.emit("update", last_message, namespace="/screen")
    emit("result", {"ok": True, "msg": "已发送"}, namespace="/send")

if __name__ == "__main__":
    # 生产可换为 socketio.run(app, host="0.0.0.0", port=8000, debug=False)
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
