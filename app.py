from flask import Flask, request, jsonify, render_template
import os
import json
import subprocess
import time

app = Flask(__name__)

# ⚙️ Update this path to match your actual local path
SHARED_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'flask_hopping_project', 'shared_data')
os.makedirs(SHARED_FOLDER, exist_ok=True)

TEXT_FILE = os.path.join(SHARED_FOLDER, 'text_message.txt')
AUDIO_FILE = os.path.join(SHARED_FOLDER, 'uploaded_audio.wav')
FLAGS_FILE = os.path.join(SHARED_FOLDER, 'simulation_flags.json')
CONFIG_FILE = os.path.join(SHARED_FOLDER, 'hopping_config.json')


# 🔁 Auto Git Sync after updates
def auto_git_sync():
    try:
        subprocess.call(["git", "add", "."], shell=True)
        commit_msg = f"Auto-sync: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.call(["git", "commit", "-m", commit_msg], shell=True)
        subprocess.call(["git", "push"], shell=True)
        print("✅ Auto Git sync complete.")
    except Exception as e:
        print(f"❌ Git sync failed: {e}")


# 🏠 UI
@app.route('/')
def index():
    return render_template('index.html')


# 📝 Send Encrypted Text
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

        auto_git_sync()
        return "✅ Text encrypted and saved."
    except Exception as e:
        return f"❌ Error saving text: {e}"


# 🎵 Upload Audio File
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        audio = request.files['audio']
        audio.save(AUDIO_FILE)
        auto_git_sync()
        return "✅ Audio uploaded."
    except Exception as e:
        return f"❌ Error uploading audio: {e}"


# 🛡️ Set Simulation Flags
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

        auto_git_sync()
        return jsonify({"status": "flags saved"}), 200
    except Exception as e:
        return jsonify({"status": f"error saving flags: {e}"}), 400


# 🔁 Set Hopping Parameters
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

        auto_git_sync()
        return "✅ Hopping config saved."
    except Exception as e:
        return f"❌ Error saving config: {e}"


# 🚀 Run App
if __name__ == '__main__':
    app.run(debug=True)
