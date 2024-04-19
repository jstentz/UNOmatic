from flask import Blueprint, render_template, request, make_response

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")


# receives the state from
@main.route("/from_pi", methods=['POST'])
def handle_state():
    response = make_response('Success!', 200)
    return response