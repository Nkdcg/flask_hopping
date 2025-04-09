from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# 📁 Shared folder path
SHARED_FOLDER = os.path.join(os.getcwd(), "shared_data")
os.makedirs(SHARED_FOLDER, exist_ok=True)

# 🔐 XOR Encryption
def xor_encrypt(text, key):
    encrypted = bytearray()
    for i, char in enumerate(text):
        encrypted_char = ord(char) ^ ord(key[i % len(key)])
        encrypted.append(encrypted_char)
    return encrypted

# ⬆️ Push file to GitHub
def push_to_github(filename, commit_message):
    os.chdir(os.getcwd())
    os.system(f'git add shared_data/{filename}')
    os.system(f'git commit -m "{commit_message}"')
    os.system('git push origin main')

# 🏠 Home route
@app.route('/')
def index():
    return render_template('index.html')

# ✉️ Send encrypted text
@app.route('/send_text', methods=['POST'])
def send_text():
    text = request.form.get('text')
    key = 'eceproject2025'
    encrypted = xor_encrypt(text, key)

    text_path = os.path.join(SHARED_FOLDER, 'text_message.txt')
    with open(text_path, 'wb') as f:
        f.write(encrypted)

    push_to_github('text_message.txt', 'Update encrypted text')
    return '✅ Text encrypted & pushed to GitHub.'

# 🎵 Upload audio
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return "❌ No audio file part", 400
    audio = request.files['audio']
    audio_path = os.path.join(SHARED_FOLDER, 'uploaded_audio.wav')
    audio.save(audio_path)

    push_to_github('uploaded_audio.wav', 'Update audio file')
    return "✅ Audio uploaded & pushed to GitHub."

# 🛡️ Save simulation flags
@app.route('/set_simulation_flags', methods=['POST'])
def set_simulation_flags():
    data = request.get_json()
    flags = {
        "simulate_jamming": data.get("simulate_jamming", False),
        "simulate_eavesdropping": data.get("simulate_eavesdropping", False)
    }

    flags_path = os.path.join(SHARED_FOLDER, 'simulation_flags.json')
    with open(flags_path, 'w') as f:
        json.dump(flags, f)

    push_to_github('simulation_flags.json', 'Update simulation flags')
    return jsonify({"status": "✅ Simulation flags saved & pushed to GitHub."})

# 🚀 Run Flask
if __name__ == '__main__':
    app.run(debug=True)
