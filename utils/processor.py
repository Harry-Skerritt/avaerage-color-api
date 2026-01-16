import requests
from PIL import Image
from io import BytesIO
import colorsys
import numpy as np
from sklearn.cluster import KMeans

class ColourProcessor:
    @staticmethod
    def get_image(url):
        headers = {'User-Agent': "Mozilla/5.0"}
        resp = requests.get(url, timeout=5, headers=headers)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGB")

    @staticmethod
    def rgb_to_hex(r, g, b):
        # Using your original 0x format for average/vibrant
        return f"0x{int(r):02x}{int(g):02x}{int(b):02x}"

    @staticmethod
    def get_shades(r, g, b):
        # Your original HLS shade logic
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
        def adjust_l(delta):
            new_l = max(0, min(1, l + delta))
            nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
            return ColourProcessor.rgb_to_hex(nr * 255, ng * 255, nb * 255)

        return {
            "lighter_1": adjust_l(0.1),
            "lighter_2": adjust_l(0.2),
            "darker_1": adjust_l(-0.1),
            "darker_2": adjust_l(-0.2)
        }

    @classmethod
    def analyze(cls, url, mode='average'):
        img = cls.get_image(url)
        if mode == 'average':
            img_avg = img.resize((1, 1), resample=Image.Resampling.LANCZOS)
            r, g, b = img_avg.getpixel((0, 0))
        else:
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

    @classmethod
    def analyze_spotify(cls, url):

        img = cls.get_image(url)
        img.thumbnail((100, 100))
        pixels = np.array(img).reshape(-1, 3)

        # Extraction via K-Means
        kmeans = KMeans(n_clusters=8, n_init=10).fit(pixels)
        clusters = kmeans.cluster_centers_

        best_color = None
        max_score = -1

        for color in clusters:
            r_norm, g_norm, b_norm = color / 255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

            sat_weight = s ** 2
            val_weight = 1.0 - abs(v - 0.5)

            score = sat_weight * val_weight

            if score > max_score:
                max_score = score
                best_color = color

        if best_color is None:
            best_color = clusters[0]

        r, g, b = [int(c) for c in best_color]
        r1, g1, b1 = [int(c * 0.7) for c in best_color]

        results = {
            "spotify": cls.rgb_to_hex(r, g, b),
            "spotify-darker": cls.rgb_to_hex(r1, g1, b1)
        }

        results.update(cls.get_shades(r1, g1, b1))

        return results




