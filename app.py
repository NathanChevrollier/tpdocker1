import random
from flask import Flask, jsonify
from pathlib import Path

QUOTES = [
"Docker vous donne l'isolement sans la douleur des VM.",
"Build once, run anywhere (du moins en théorie).",
"Les couches de Docker sont des caches déguisés.",
]
app = Flask(__name__)
@app.get("/quote")
def quote():
    return jsonify({"quote": random.choice(QUOTES)})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


def load_quotes():
    with Path("data/quotes.txt").open() as fh:
        return [line.strip() for line in fh if line.strip()]
QUOTES = load_quotes()