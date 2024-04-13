import os

from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

state = ""

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        data = request.form["num"]
        return render_template("index.html", content=data)
    return render_template("index.html", content="ello")



if __name__ == "__main__":
    app.run(debug=True)

