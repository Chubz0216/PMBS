document.getElementById('generate-barcode').addEventListener('click', function() {
    var barcode = document.getElementById('barcode').value;

    // Check if barcode is empty
    if (!barcode) {
        alert("Please enter a barcode.");
        return;
    }

    // Log to console for debugging
    console.log("Generating barcode for:", barcode);

    // Generate barcode URL using Code128
    var barcodeImageSrc = `https://barcode.tec-it.com/barcode.ashx?data=${barcode}&code=Code128&translate-esc=true`;

    // Set the barcode image
    document.getElementById('barcode-image').src = barcodeImageSrc;
});
