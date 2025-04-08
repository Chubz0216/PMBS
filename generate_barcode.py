import barcode
from barcode.writer import ImageWriter

def generate_custom_barcode(data, output_path):
    # Piliin ang Code39 format
    code128 = barcode.get_barcode_class('code128')

    # Gumawa ng barcode object
    barcode_obj = code39(data, writer=ImageWriter())

    # I-customize ang options ng barcode (kasama na ang text size)
    options = {
        'text_distance': 5,  # Distansya ng text mula sa barcode
        'font_size': 10,     # Mas maliit na font size para sa text
        'show_text': True,   # Ipakita pa rin ang text
    }

    # I-save ang image ng barcode
    barcode_obj.save(output_path, options=options)

# Example usage
generate_custom_barcode('A12345', 'custom_code39_barcode')
