# routes/barcode_preview.py

from flask import Blueprint, request, send_file
from utils.custom_barcode import create_ean13_image

barcode_preview = Blueprint('barcode_preview', __name__)

@barcode_preview.route('/preview_barcode')
def preview_barcode():
    code = request.args.get('code')
    name = request.args.get('name')
    price = request.args.get('price')

    if not code or not name or not price:
        return "Missing parameters", 400

    image_io, full_code = create_ean13_image(code, name, price)
    return send_file(image_io, mimetype='image/png')
