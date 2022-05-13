from flask import request, jsonify, Response, render_template
from abot import app
from abot.models import *
from abot.messageProcessor import SpanishMessageProcessor
from flask_cors import cross_origin


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["GET"])
@cross_origin()
def availability():
    return Response(status=200)


@app.route("/api/bot", methods=["POST"])
@cross_origin()
def bot():
    req_data = request.get_json()
    processor = SpanishMessageProcessor(req_data["message"])
    processor.process_message()
    response = jsonify(processor.bot_response)
    return response


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": True, "message": "No conocemos este endpoint :("}), 404
