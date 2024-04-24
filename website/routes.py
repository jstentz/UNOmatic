from flask import Blueprint, render_template, request, redirect
from flask_socketio import emit

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/reset", methods=['POST'])
def handle_reset():
    print("yipee")
    print(request.form["num_players"])
    print(request.form["num_cards"])
    emit("reset", {"num_players" : request.form["num_players"], "num_cards" : request.form["num_cards"]}, namespace="/", broadcast=True)
    return redirect("/")

@main.route("/round_reset", methods=['POST'])
def handle_round_reset():
    print("yipee_round_reset")
    emit("round_reset", namespace="/", broadcast=True)
    return redirect("/")
