from PIL import Image, ImageDraw, ImageFont
import io

# EAN-13 encoding tables
L_CODES = {
    '0': '0001101', '1': '0011001', '2': '0010011',
    '3': '0111101', '4': '0100011', '5': '0110001',
    '6': '0101111', '7': '0111011', '8': '0110111',
    '9': '0001011'
}

R_CODES = {
    '0': '1110010', '1': '1100110', '2': '1101100',
    '3': '1000010', '4': '1011100', '5': '1001110',
    '6': '1010000', '7': '1000100', '8': '1001000',
    '9': '1110100'
}

GUARD_BARS = {
    'start': '101',
    'middle': '01010',
    'end': '101'
}

def calculate_ean13_checksum(code):
    digits = [int(d) for d in code]
    even = sum(digits[-1::-2])
    odd = sum(digits[-2::-2])
    total = even + odd * 3
    return str((10 - (total % 10)) % 10)

def create_ean13_image(code12, name, price):
    if len(code12) != 12 or not code12.isdigit():
        raise ValueError("Code must be 12 digits")

    full_code = code12 + calculate_ean13_checksum(code12)

    # Build binary barcode
    left = ''.join([L_CODES[d] for d in full_code[1:7]])
    right = ''.join([R_CODES[d] for d in full_code[7:]])
    binary_code = GUARD_BARS['start'] + left + GUARD_BARS['middle'] + right + GUARD_BARS['end']

    bar_width = 3
    bar_height = 70
    guard_bar_extra = 15
    text_height = 40
    white_margin = 30
    top_margin = 10
    total_width = (len(binary_code) * bar_width) + white_margin * 2
    image_height = bar_height + guard_bar_extra + text_height + 40

    img = Image.new("RGB", (total_width, image_height), "white")
    draw = ImageDraw.Draw(img)

    # Try to load proper fonts
    try:
        font_digit = ImageFont.truetype("arialbd.ttf", 25)
        font_price = ImageFont.truetype("arialbd.ttf", 28)
        font_name = ImageFont.truetype("arialbd.ttf", 20)

    except IOError:
        font_digit = font_price = font_name = ImageFont.load_default()

        # Adjust the text positioning to be closer to the barcode
        text_y = bar_height + guard_bar_extra - 0
        for x, digit in digit_positions:
            draw.text((x, text_y), digit, font=font_digit, fill="black")



    # Draw bars
    x_offset = white_margin
    middle_guard_index = len(GUARD_BARS['start']) + len(left)
    for i, bit in enumerate(binary_code):
        x = x_offset + i * bar_width
        y = top_margin  # Start drawing bars after the top margin
        h = bar_height
        if i < 3 or (middle_guard_index <= i <= middle_guard_index + 4) or (i >= len(binary_code) - 3):
            h += guard_bar_extra
        if bit == '1':
            draw.rectangle([x, y, x + bar_width - 1, y + h], fill="black")

    # Barcode number text placement
    digit_positions = []
    # First digit (outside left)
    first_digit_x = white_margin + (0 * bar_width) - 18
    digit_positions.append((first_digit_x, full_code[0]))

    # 6 digits on the left side
    for i in range(6):
        left_start = white_margin + (3 + i * 7) * bar_width
        digit_positions.append((left_start + bar_width * 2, full_code[1 + i]))

    # 6 digits on the right side
    for i in range(6):
        right_start = white_margin + (3 + 42 + 5 + i * 7) * bar_width
        digit_positions.append((right_start + bar_width * 2, full_code[7 + i]))

    # Adjust the text positioning to be closer to the barcode
    text_y = bar_height + guard_bar_extra - 5
    for x, digit in digit_positions:
        draw.text((x, text_y), digit, font=font_digit, fill="black")

    # Product name and price below barcode
    price_x = 10  # adjust mo ito para lumapit sa kaliwa
    name_x = 10  # same here

    draw.text((price_x, text_y + 25), f"₱ {price}.00", font=font_price, fill="black")
    draw.text((name_x, text_y + 55), name, font=font_name, fill="black")

    # Save image
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer, full_code
