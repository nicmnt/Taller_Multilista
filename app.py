from flask import Flask, jsonify, render_template
from multilista import MultiList

app = Flask(__name__)
multilista = MultiList.from_csv("DIVIPOLA.csv")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/multilista")
def api_multilista():
    return jsonify(multilista.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
