from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
SHARED_FOLDER = os.path.join(os.getcwd(), "shared_data")
os.makedirs(SHARED_FOLDER, exist_ok=True)

# XOR Encryption function
def xor_encrypt(text, key):
    encrypted = bytearray()
    for i, char in enumerate(text):
        encrypted_char = ord(char) ^ ord(key[i % len(key)])
        encrypted.append(encrypted_char)
    return encrypted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_text', methods=['POST'])
def send_text():
    text = request.form.get('text')
    key = 'eceproject2025'

    encrypted = xor_encrypt(text, key)
    with open(os.path.join(SHARED_FOLDER, 'text_message.txt'), 'wb') as f:
        f.write(encrypted)

    return '✅ Text encrypted & saved successfully.'

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return "❌ No audio file part", 400
    audio = request.files['audio']
    audio.save(os.path.join(SHARED_FOLDER, 'uploaded_audio.wav'))
    return "✅ Audio uploaded successfully."

if __name__ == '__main__':
    app.run(debug=True)
