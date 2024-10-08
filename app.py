import os
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)


def get_latest_csv():
    completions_dir = "datasets/completions/"
    csv_files = [f for f in os.listdir(completions_dir) if f.endswith(".csv")]
    if not csv_files:
        return None
    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(completions_dir, f)))
    return os.path.join(completions_dir, latest_file)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    csv_file = get_latest_csv()
    if not csv_file:
        return jsonify({"error": "No CSV file found"}), 404

    df = pd.read_csv(csv_file)
    data = df[["id", "question", "stepped", "perturbed", "step", "type", "trace", "completion"]].to_dict("records")
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
