from flask import Flask, request, jsonify
import requests
from PIL import Image
from io import BytesIO
import colorsys


app = Flask(__name__)

def rgb_to_hex(r, g, b):
	# Formats as 0xRRGGBB
	return f"0x{int(r):02x}{int(g):02x}{int(b):02x}"

def get_shade(r, g, b, delta):
	# Converts RGB to HLS
	h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
	
	new_l = max(0, min(1, l + delta))
	new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)
	return rgb_to_hex(new_r * 255, new_g * 255, new_b * 255)


@app.route('/api/analyse', methods=['GET'])
def analyse():
	img_url = request.args.get('url')
	if not img_url:
		return jsonify({"error": "No URL provided"}), 400

	try:
		# Fetch image
		headers = {'User-Agent': "Mozilla/5.0"}
		resp = requests.get(img_url, timeout=5, headers=headers)
		resp.raise_for_status()


		img = Image.open(BytesIO(resp.content)).convert("RGB")
		
		img = img.resize((1, 1), resample=Image.Resampling.LANCZOS)
		r, g, b = img.getpixel((0, 0))

		return jsonify({
			"average": rgb_to_hex(r, g, b),
			"lighter_1": get_shade(r, g, b, 0.1),
			"lighter_2": get_shade(r, g, b, 0.2),
			"darker_1": get_shade(r, g, b, -0.1),
			"darker_2": get_shade(r, g, b, -0.2)
		})

	except Exception as e:
		return jsonify({"error": "Processing failed", "details": str(e)}), 500


app = app
