from http.server import BaseHTTPRequestHandler
import json
import rasterio
from rasterio.windows import Window
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        tif_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mapa.tif')

        output_folder = '/tmp/quadrants'
        os.makedirs(output_folder, exist_ok=True)

        quadrants = []

        with rasterio.open(tif_path) as src:
            width = src.width
            height = src.height

            half_width = width // 2
            half_height = height // 2

            windows = {
                'top_left': Window(0, 0, half_width, half_height),
                'top_right': Window(half_width, 0, half_width, half_height),
                'bottom_left': Window(0, half_height, half_width, half_height),
                'bottom_right': Window(half_width, half_height, half_width, half_height)
            }

            for name, window in windows.items():
                transform = src.window_transform(window)
                data = src.read(window=window)

                output_path = os.path.join(output_folder, f'{name}.tif')

                profile = src.profile
                profile.update({
                    'height': int(window.height),
                    'width': int(window.width),
                    'transform': transform
                })

                with rasterio.open(output_path, 'w', **profile) as dst:
                    dst.write(data)

                quadrants.append({
                    'name': name,
                    'file': output_path
                })

        response = {
            'message': 'TIFF dividido correctamente',
            'quadrants': quadrants
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())