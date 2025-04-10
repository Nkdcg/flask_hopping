from flask import Flask, request, jsonify, render_template
import os
import json
import subprocess
from datetime import datetime

app = Flask(__name__)
SHARED_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'flask_hopping_project', 'shared_data')
os.makedirs(SHARED_FOLDER, exist_ok=True)

TEXT_FILE = os.path.join(SHARED_FOLDER, 'text_message.txt')
AUDIO_FILE = os.path.join(SHARED_FOLDER, 'uploaded_audio.wav')
FLAGS_FILE = os.path.join(SHARED_FOLDER, 'simulation_flags.json')
CONFIG_FILE = os.path.join(SHARED_FOLDER, 'hopping_config.json')

GIT_REPO_PATH = os.path.abspath(os.path.join(SHARED_FOLDER, '..'))

def auto_git_push(commit_msg):
    try:
        subprocess.run(["git", "add", "."], cwd=GIT_REPO_PATH, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=GIT_REPO_PATH, check=True)
        subprocess.run(["git", "push"], cwd=GIT_REPO_PATH, check=True)
        print("✅ Auto-pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

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

        auto_git_push(f"🔒 Encrypted text committed @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Text encrypted, saved and pushed."
    except Exception as e:
        return f"❌ Error saving text: {e}"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        audio = request.files['audio']
        audio.save(AUDIO_FILE)
        auto_git_push(f"🔊 Audio uploaded @ {datetime.now().strftime('%H:%M:%S')}")
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

        auto_git_push(f"🚨 Simulation flags updated @ {datetime.now().strftime('%H:%M:%S')}")
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

        auto_git_push(f"⚙️ Hopping config updated @ {datetime.now().strftime('%H:%M:%S')}")
        return "✅ Hopping config saved and pushed."
    except Exception as e:
        return f"❌ Error saving config: {e}"

if __name__ == '__main__':
    app.run(debug=True)
