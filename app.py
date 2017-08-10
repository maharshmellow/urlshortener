from flask import Flask, jsonify, render_template, request, redirect
import hashlib
import validators
from pymongo import MongoClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

@app.route("/")
@limiter.exempt
def index():
    return render_template("home.html")

@app.route("/shorten", methods=["POST"])
@limiter.limit("60/hour")
def shorten():
    if request.method == "POST":
        try:
            url = request.values.get("url")
            if not url or not validators.url(url):
                raise

            code = hashlib.sha256(url.encode("utf-8")).hexdigest()[:5]
        except:
            return jsonify({"status": 0, "shortened_url":""})


        shortened_url = "url.maharsh.net/" + code

        # add to the database
        data = {}
        data["url"] = url
        data["_id"] = code
        client = MongoClient(os.environ.get("MONGO_URL"))
        db = client.get_default_database()
        urls = db["urls"]

        try:
            urls.insert_one(data)
        except:
            pass
        return jsonify({"status": 1, "shortened_url":shortened_url})

@app.route("/<code>")
def redirect_code(code):
    client = MongoClient(os.environ.get("MONGO_URL"))
    db = client.get_default_database()
    urls = db["urls"]

    match = urls.find_one({"_id":code})
    if match:

        return redirect(match["url"])
    return render_template("home.html")


if __name__ == "__main__":
    app.run()
