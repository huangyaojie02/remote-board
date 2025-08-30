# 远程文字留言板（iPad 显示版）

## 快速开始
1. 安装 Python 3.10+
2. 终端进入本目录：`cd remote-board`
3. 安装依赖：`pip install -r requirements.txt`
4. 设置发送端令牌：
   - macOS/Linux: `export SENDER_TOKEN="your_super_secret_token"`
   - Windows PowerShell: `$env:SENDER_TOKEN="your_super_secret_token"`
5. 启动：`python app.py`
6. 手机（发送端）访问：`http://<你的IP>:8000/send?t=your_super_secret_token`
7. iPad（显示端）访问：`http://<你的IP>:8000/screen`，并添加到主屏幕

> `<你的IP>` 在同一 Wi‑Fi 下用 `ipconfig`（Windows）或 `ipconfig getifaddr en0`（macOS）查看。
