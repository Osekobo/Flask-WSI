from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
  res = {"Flask API Version" : "1.0"}
  return jsonify(res), 200

app.run()