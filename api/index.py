from flask import Flask, request, jsonify
import requests
from PIL import Image
from io import BytesIO
import colorsys

app = Flask(__name__)

@app.route('/api/average')
def api_average():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        return jsonify(ColourProcessor.analyze(url, 'average'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vibrant')
def api_vibrant():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        return jsonify(ColourProcessor.analyze(url, 'vibrant'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/spotifybackground")
def api_spotify():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        return jsonify(ColourProcessor.analyze_spotify(url))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel detection
app = app
