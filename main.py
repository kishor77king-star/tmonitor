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
                x = x.replace("\n", "")
                if x.isdigit():
                    to_return.append(int(x))
                elif x[0].isdigit() and not x[1:].isdigit():
                    pass
                else:
                    to_return.append(x)
            return to_return
    except FileNotFoundError:
        return []

##### load settings
with open("settings.conf", "r") as f:
    data = f.readlines()

[data.remove(x) for x in data if x == "\n"]
data = [x.replace("\n", "") for x in data
