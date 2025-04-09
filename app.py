from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    text = data.get("text", "")
    print("Received:", text)
    response = f"Message received: {text}"
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
