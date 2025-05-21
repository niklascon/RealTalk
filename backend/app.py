from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
last_result = {"keyword": "", "text": ""}

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/current')
def current():
    return render_template('current.html', last_result=last_result)

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/api/log', methods=['POST'])
def log_result():
    data = request.json
    last_result["keyword"] = data.get("keyword", "")
    last_result["text"] = data.get("text", "")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

