import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters

# --- DUMMY WEB SERVER FOR RENDER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# -----------------------------------

def save_list(to_save):
    if to_save == "monitor" or to_save == "m":
        to_save = ["monitor", monitor_list]
    elif to_save == "forward" or to_save == "fwd":
        to_save = ["forward", forward_list]
    else:
        raise ValueError
    with open(to_save[0]+".list", "w") as f:
        f.write("\n".join([str(x) for x in to_save[1]])+"\n")

def load_list(to_load):
    if not to_load.endswith(".list"): to_load = to_load + ".list"
    if to_load == "monitor.list" or to_load == "m.list":
        to_load = "monitor.list"
    elif to_load == "forward.list" or to_load == "fwd.list":
        to_load = "forward.list"
    else:
        raise ValueError
    try:
        with open(to_load, "r") as f:
            to_return = []
            for x in f.readlines():
                x = x.strip()
                if not x: continue
                try:
                    # Fix: Correctly parses negative IDs like -100...
                    to_return.append(int(x))
                except ValueError:
                    to_return.append(x)
            return to_return
    except FileNotFoundError:
        return []

##### load settings
with open("settings.conf", "r") as f:
    data = f.readlines()

[data.remove(x) for x in data if x == "\n"]
data = [x.replace("\n", "") for x in data]
data = [x.split("#")[0] for x in data]
data = [x.split("=") for x in data]

settings = {}
for x, y in data:
    y = y.strip()
    if y.isdigit(): y = int(y)
    settings[x] = y

if settings["command_prefix"] == "\eq": settings["command_prefix"] = "="
#####

session_code = os.environ.get("SESSION")

app = Client("tmonitor_bot",
        session_string=session_code,
        api_id=settings["api_id"],
        api_hash=settings["api_hash"]
        )

monitor_list = load_list("m")
forward_list = load_list("fwd")

try:
    @app.on_message(filters.create(lambda _, __, x: x.chat and (x.chat.username in monitor_list or x.chat.id in monitor_list)))
    def fwd(client, message):
        for chat in forward_list:
            try:
                if isinstance(chat, int) or (isinstance(chat, str) and chat.startswith("-100")):
                    message.forward(int(chat))
                else:
                    message.forward(f"@{chat}")
            except Exception as e:
                pass

    @app.on_message(filters.me & filters.command(["monitor", "m"], settings["command_prefix"]))
    def monitoradd(client, message):
        global monitor_list
        if len(message.text.split()) == 1:
            if message.chat.id in monitor_list:
                message.reply("No duplicates")
            else:
                monitor_list.append(message.chat.id)
                save_list("m")
                message.reply("Ok")
        else:
            name = message.text.split()[1]
            try:
                name = int(name)
            except ValueError:
                pass
            
            if name in monitor_list:
                message.reply("No duplicates")
            else:
                monitor_list.append(name)
                save_list("m")
                message.reply("Ok")

    @app.on_message(filters.me & filters.command(["forward", "fwd"], settings["command_prefix"]))
    def fwdadd(client, message):
        global forward_list
        if len(message.text.split()) == 1:
            message.reply("Not enough args")
        else:
            name = message.text.split()[1]
            try:
                name = int(name)
            except ValueError:
                pass

            if name in forward_list:
                message.reply("No duplicates")
            else:
                forward_list.append(name)
                save_list("fwd")
                message.reply("Ok")
except Exception as e:
    print("Error:", e)

app.run()
