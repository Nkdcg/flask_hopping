from flask import Flask, request, jsonify, render_template
import os
import json
import base64
import requests
from datetime import datetime

app = Flask(__name__)
SHARED_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'flask_hopping_project', 'shared_data')
os.makedirs(SHARED_FOLDER, exist_ok=True)

TEXT_FILE = os.path.join(SHARED_FOLDER, 'text_message.txt')
AUDIO_FILE = os.path.join(SHARED_FOLDER, 'uploaded_audio.wav')
FLAGS_FILE = os.path.join(SHARED_FOLDER, 'simulation_flags.json')
CONFIG_FILE = os.path.join(SHARED_FOLDER, 'hopping_config.json')

# GitHub API Push Setup
GITHUB_USER = "Nkdcg"
REPO_NAME = "flask_hopping"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN")  # Make sure this is set in Render environment
GITHUB_API = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/shared_data"

# === Upload File to GitHub via API ===
def github_api_push(filename, local_path, commit_msg):
    try:
        url = f"{GITHUB_API}/{filename}"
        headers = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        # Read local content
        with open(local_path, 'rb') as f:
            content = f.read()

        encoded = base64.b64encode(content).decode('utf-8')

        # Check if file already exists to get SHA
        sha = None
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json().get('sha')

        data = {
            "message": commit_msg,
            "content": encoded,
            "branch": BRANCH
        }
        if sha:
            data["sha"] = sha

        res = requests.put(url, headers=headers, json=data)
        if res.status_code in [200, 201]:
            print(f"✅ {filename} pushed to GitHub.")
        else:
            print(f"❌ Failed to push {filename}:", res.text)
    except Exception as e:
        print(f"❌ Exception pushing {filename}:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_text', methods=['POST'])
def send_text():
    try:
        text = request.form['text']
        key = 'eceproject2025'
        encrypted = bytearray()
        for i, char in enumerate(text):
            encrypted_char = ord(char) ^ ord(key[i % len(key)])
            encrypted.append(encrypted_char)

        with open(TEXT_FILE, 'wb') as f:
            f.write(encrypted)

        github_api_push('text_message.txt', TEXT_FILE, f"🔒 Encrypted text @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Text encrypted, saved, and pushed."
    except Exception as e:
        return f"❌ Error saving text: {e}"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        audio = request.files['audio']
        audio.save(AUDIO_FILE)
        github_api_push('uploaded_audio.wav', AUDIO_FILE, f"🔊 Audio uploaded @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Audio uploaded and pushed."
    except Exception as e:
        return f"❌ Error uploading audio: {e}"

@app.route('/set_simulation_flags', methods=['POST'])
def set_simulation_flags():
    try:
        data = request.get_json(force=True)
        flags = {
            "simulate_jamming": bool(data.get("simulate_jamming", False)),
            "simulate_eavesdropping": bool(data.get("simulate_eavesdropping", False))
        }
        with open(FLAGS_FILE, 'w') as f:
            json.dump(flags, f)

        github_api_push('simulation_flags.json', FLAGS_FILE, f"🚨 Flags updated @ {datetime.now().strftime('%H:%M:%S')}")
        return jsonify({"status": "flags saved"}), 200
    except Exception as e:
        return jsonify({"status": f"error saving flags: {e}"}), 400

@app.route('/set_hopping_config', methods=['POST'])
def set_hopping_config():
    try:
        start_freq = int(request.form['start_freq'])
        hop_interval = float(request.form['hop_interval'])
        config = {
            "start_freq": start_freq,
            "hop_interval": hop_interval
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

        github_api_push('hopping_config.json', CONFIG_FILE, f"⚙️ Config updated @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Config saved and pushed."
    except Exception as e:
        return f"❌ Error saving config: {e}"

if __name__ == '__main__':
    app.run(debug=True)
