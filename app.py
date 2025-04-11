from flask import Flask, request, jsonify, render_template
import os
import json
import base64
import requests
from datetime import datetime

app = Flask(__name__)

# === File & Repo Configuration ===
SHARED_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'flask_hopping_project', 'shared_data')
os.makedirs(SHARED_FOLDER, exist_ok=True)

TEXT_FILE = os.path.join(SHARED_FOLDER, 'text_message.txt')
AUDIO_FILE = os.path.join(SHARED_FOLDER, 'uploaded_audio.wav')
FLAGS_FILE = os.path.join(SHARED_FOLDER, 'simulation_flags.json')
CONFIG_FILE = os.path.join(SHARED_FOLDER, 'hopping_config.json')

GITHUB_USERNAME = "Nkdcg"
REPO_NAME = "flask_hopping"
BRANCH = "main"

# === Push File to GitHub ===
def github_api_push(file_path, commit_message):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not set in environment.")
        return

    file_name = os.path.basename(file_path)
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/shared_data/{file_name}"

    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            encoded = base64.b64encode(content).decode()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        sha = None
        get_response = requests.get(api_url, headers=headers)
        if get_response.status_code == 200:
            sha = get_response.json().get('sha')

        payload = {
            "message": commit_message,
            "content": encoded,
            "branch": BRANCH
        }
        if sha:
            payload["sha"] = sha

        put_response = requests.put(api_url, headers=headers, json=payload)

        if put_response.status_code in [200, 201]:
            print(f"✅ {file_name} pushed to GitHub.")
        else:
            print(f"❌ Failed to push {file_name}: {put_response.text}")

    except Exception as e:
        print(f"❌ Exception during GitHub push: {e}")

# === Flask Routes ===
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
            encrypted.append(ord(char) ^ ord(key[i % len(key)]))

        with open(TEXT_FILE, 'wb') as f:
            f.write(encrypted)

        github_api_push(TEXT_FILE, f"🔒 Encrypted text committed @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Text encrypted and pushed to GitHub."
    except Exception as e:
        return f"❌ Error saving text: {e}"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        audio = request.files['audio']
        audio.save(AUDIO_FILE)

        github_api_push(AUDIO_FILE, f"🔊 Audio uploaded @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Audio uploaded and pushed to GitHub."
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

        github_api_push(FLAGS_FILE, f"🚨 Simulation flags updated @ {datetime.now().strftime('%H:%M:%S')}")
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

        github_api_push(CONFIG_FILE, f"⚙️ Hopping config updated @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Hopping config saved and pushed to GitHub."
    except Exception as e:
        return f"❌ Error saving config: {e}"

# === Run Flask App ===
if __name__ == '__main__':
    app.run(debug=True)
