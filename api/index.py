from flask import Flask, request, jsonify
import requests
from PIL import Image
from io import BytesIO
import colorsys


app = Flask(__name__)


class ColourProcessor:
	@staticmethod
	def get_image(url):
		headers = {'User-Agent': "Mozilla/5.0"}
		resp = requests.get(img_url, timeout=5, headers=headers)
		resp.raise_for_status()
		return Image.open(BytesIO(resp.content)).convert("RGB")

	@staticmethod
	def rgb_to_hex(r, g, b):
		# Formats as 0xRRGGBB
		return f"0x{int(r):02x}{int(g):02x}{int(b):02x}"

	@staticmethod
	def get_shade(r, g, b, delta):
		# Converts RGB to HLS
		h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
	
		def adjust_l(delta):
            new_l = max(0, min(1, l + delta))
            nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
            return ColorProcessor.rgb_to_hex(nr * 255, ng * 255, nb * 255)

		return {
            "lighter_1": adjust_l(0.1),
            "lighter_2": adjust_l(0.2),
            "darker_1": adjust_l(-0.1),
            "darker_2": adjust_l(-0.2)
        }

	@classmethod
	def analyze(cls, img_url, mode='average'):
        img = cls.get_image(img_url)

        if mode == 'average':
            img_avg = img.resize((1, 1), resample=Image.Resampling.LANCZOS)
            r, g, b = img_avg.getpixel((0, 0))
        else:
            # Vibrant mode
            img.thumbnail((50, 50))
            pixels = list(img.getdata())
            best_pixel = (0, 0, 0)
            max_score = -1
            for pr, pg, pb in pixels:
                h, l, s = colorsys.rgb_to_hls(pr/255.0, pg/255.0, pb/255.0)
                score = s * (1 - abs(2 * l - 1))
                if score > max_score:
                    max_score = score
                    best_pixel = (pr, pg, pb)
            r, g, b = best_pixel

        results = {mode: cls.rgb_to_hex(r, g, b)}
        results.update(cls.get_shades(r, g, b))
        return results


@app.route('/api/average')
def api_average():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        return jsonify(ColorProcessor.analyze(url, 'average'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vibrant')
def api_vibrant():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        return jsonify(ColorProcessor.analyze(url, 'vibrant'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


app = app
