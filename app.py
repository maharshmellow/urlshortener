from flask import Flask, jsonify, render_template, request, redirect
import hashlib
import validators
from pymongo import MongoClient

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/shorten", methods=["POST"])
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
        client = MongoClient("mongodb://temp:temp@ds125113.mlab.com:25113/heroku_url")
        db = client.get_default_database()
        urls = db["urls"]

        try:
            urls.insert_one(data)
        except:
            pass
        return jsonify({"status": 1, "shortened_url":shortened_url})

@app.route("/<code>")
def redirect_code(code):
    client = MongoClient("mongodb://temp:temp@ds125113.mlab.com:25113/heroku_url")
    db = client.get_default_database()
    urls = db["urls"]

    match = urls.find_one({"_id":code})
    if match:

        return redirect(match["url"])
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
