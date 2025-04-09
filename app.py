from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import sqlite3
import io
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        price = request.form['price']

        conn = get_db_connection()
        conn.execute('INSERT INTO products (barcode, name, price) VALUES (?, ?, ?)',
                     (barcode, name, price))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route("/generate_barcode")
def generate_barcode():
    data = request.args.get("data")
    price = request.args.get("price")
    name = request.args.get("name")

    if not all([data, price, name]):
        return "Missing data", 400

    # Barcode image generation with custom width
    barcode_img_io = io.BytesIO()
    options = {
        'module_width': 0.5,  # Increase the width of the barcode
    }
    barcode = Code128(data, writer=ImageWriter())
    barcode.write(barcode_img_io, options=options)
    barcode_img_io.seek(0)

    # Convert to PIL image
    barcode_image = Image.open(barcode_img_io)

    # Create new image with space for text
    new_height = barcode_image.height + 100  # Increase the space for text
    new_img = Image.new("RGB", (barcode_image.width, new_height), "white")
    new_img.paste(barcode_image, (0, 0))

    # Add price and name text with bigger font
    draw = ImageDraw.Draw(new_img)
    try:
        # Use bold font for price and a normal font for the product name
        font_price = ImageFont.truetype("arialbd.ttf", 43)  # Bold Arial font
        font_name = ImageFont.truetype("arial.ttf", 40)   # Regular Arial font for name
    except IOError:
        font_price = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # Add price text with the peso sign
    draw.text((10, barcode_image.height + -30), f"₱ {price}", font=font_price, fill="black")

    # Add product name text
    draw.text((10, barcode_image.height + 30), name, font=font_name, fill="black")

    # Save result to BytesIO
    final_io = io.BytesIO()
    new_img.save(final_io, format="PNG")
    final_io.seek(0)

    return send_file(final_io, mimetype="image/png")

@app.route('/print_barcode')
def print_barcode():
    # Get barcode data from the request
    data = request.args.get("data")
    price = request.args.get("price")
    name = request.args.get("name")

    if not all([data, price, name]):
        return "Missing data", 400

    # Generate barcode image
    barcode_img_io = io.BytesIO()
    barcode = Code128(data, writer=ImageWriter())
    barcode.write(barcode_img_io)
    barcode_img_io.seek(0)

    # Convert to PIL image
    barcode_image = Image.open(barcode_img_io)

    # Create new image with space for price and name text
    new_height = barcode_image.height + 50
    new_img = Image.new("RGB", (barcode_image.width, new_height), "white")
    new_img.paste(barcode_image, (0, 0))

    # Add price and name text
    draw = ImageDraw.Draw(new_img)
    try:
        # Use bold font for price and a regular font for the product name
        font_price = ImageFont.truetype("arialbd.ttf", 43)  # Bold Arial font
        font_name = ImageFont.truetype("arial.ttf", 40)  # Regular Arial font
    except IOError:
        font_price = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # Add price text with peso sign
    draw.text((10, barcode_image.height + 10), f"₱ {price}", font=font_price, fill="black")

    # Add product name text
    draw.text((10, barcode_image.height + 30), name, font=font_name, fill="black")

    # Prepare the image for printing (Windows specific)
    printer_name = win32print.GetDefaultPrinter()  # Get the default printer
    printer = win32ui.CreateDC()
    printer.CreatePrinterDC(printer_name)

    # Convert PIL image to DIB (Device Independent Bitmap)
    hdc = printer.GetHandleOutput()
    dib = ImageWin.Dib(new_img)
    dib.draw(hdc, (0, 0, new_img.width, new_img.height))

    # Send to the printer
    printer.EndDoc()

    return "Barcode sent to printer"
@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    products = [{"id": row[0], "barcode": row[1], "name": row[2], "price": row[3]} for row in rows]
    conn.close()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
