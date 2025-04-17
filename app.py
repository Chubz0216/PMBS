from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import sqlite3
import io
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin
from flask import redirect, url_for, flash
from utils.custom_barcode import create_ean13_image
from routes.barcode_preview import barcode_preview

app = Flask(__name__)

# Database connection with context manager
def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products').fetchall()
    return render_template('index.html', products=products)

def get_db_connection():
    conn = sqlite3.connect('products.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add_product', methods=['POST'])
def add_product():
    barcode = request.form['barcode']
    name = request.form['name']
    price = request.form['price']

    try:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO products (barcode, name, price) VALUES (?, ?, ?)',
                         (barcode, name, price))
            conn.commit()
        flash("Product added successfully!", "success")
        return redirect('/')
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            flash("Barcode already exists.", "error")
        else:
            flash("Database error occurred.", "error")
        return redirect('/')

@app.route("/generate_barcode")
def generate_barcode():
    data = request.args.get("data")
    price = request.args.get("price")
    name = request.args.get("name")

    if not all([data, price, name]):
        return "Missing data", 400

    try:
        # Gumamit ng custom EAN-13 image generator
        image_io, full_code = create_ean13_image(data, name, price)
    except ValueError as e:
        return str(e), 400

    return send_file(image_io, mimetype="image/png")

@app.route('/print_barcode')
def print_barcode():
    # Get barcode data from the request
    data = request.args.get("data")
    price = request.args.get("price")
    name = request.args.get("name")

    if not all([data, price, name]):
        return "Missing data", 400

    # Generate barcode image
    EAN = get_barcode_class('ean13')
    barcode = EAN(data, writer=ImageWriter())

    barcode = UPC(data, writer=ImageWriter())
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
def get_products():
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products').fetchall()
    return jsonify([{"id": row["id"], "barcode": row["barcode"], "name": row["name"], "price": row["price"]} for row in products])

@app.route('/delete/<barcode>', methods=['DELETE'])
def delete_product(barcode):
    try:
        conn = sqlite3.connect('products.db')  # adjust path
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE barcode = ?', (barcode,))
        conn.commit()
        conn.close()
        return '', 204
    except Exception as e:
        return str(e), 500

@app.route('/get_product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    with get_db_connection() as conn:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    if product:
        return jsonify({
            'id': product['id'],
            'barcode': product['barcode'],
            'name': product['name'],
            'price': product['price']
        })
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/update/<int:product_id>', methods=['POST'])


@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if request.form.get('_method') == 'PUT':
        barcode = request.form['barcode'].strip()
        name = request.form['name'].strip()
        price = request.form['price'].strip()

        # Basic validation
        errors = {}
        if not barcode:
            errors['barcode'] = 'Barcode is required.'
        if not name:
            errors['name'] = 'Name is required.'
        if not price:
            errors['price'] = 'Price is required.'
        else:
            try:
                float(price)
            except ValueError:
                errors['price'] = 'Price must be a number.'

        if errors:
            for field, error in errors.items():
                flash(f"{field.capitalize()}: {error}", "danger")
            return redirect(url_for('index'))  # or to the same form page

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET barcode = ?, name = ?, price = ?
            WHERE id = ?
        """, (barcode, name, price, product_id))
        conn.commit()
        conn.close()

        flash("Product updated successfully!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid method.", "danger")
        return redirect(url_for('index'))

app.secret_key = 'your_secret_key_here'


@app.route('/custom_barcode', methods=['POST'])
def custom_barcode():
    try:
        data = request.json
        code = data.get('code')
        name = data.get('name')
        price = data.get('price')

        if not code or not name or not price:
            return jsonify({'error': 'Missing required fields'}), 400

        img_buffer, full_code = create_ean13_image(code, name, price)

        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=f"{full_code}.png"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app.register_blueprint(barcode_preview)

if __name__ == '__main__':
    app.run(debug=True)
