import os
from flask import Flask
if os.path.exists("env.py"):
    import os


app = Flask(__name__)


@app.route("/")
def test():
    return "Success!! You Flask app is working correctly!"


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
