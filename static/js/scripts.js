


document.addEventListener("DOMContentLoaded", function () {
            const generateBtn = document.getElementById('generate-barcode');
            const barcodeText = document.getElementById('barcode-text');
            const barcodeImage = document.getElementById('barcode-image');
            const overlay = document.getElementById('barcode-overlay');
            const searchInput = document.getElementById('search');
            const clearListBtn = document.getElementById('clear-list');
            const sortSelect = document.getElementById('sort-by');
            const productListContainer = document.getElementById('product-list');

            let productList = []; // This will hold the product data from products.db

            generateBtn.addEventListener('click', function () {
                const barcode = document.getElementById('barcode').value.trim();
                const price = document.getElementById('price').value.trim();
                const name = document.getElementById('name').value.trim();

                if (barcode && price && name) {
                    const url = `/generate_barcode?data=${encodeURIComponent(barcode)}&price=${encodeURIComponent(price)}&name=${encodeURIComponent(name)}`;
                    barcodeImage.src = url;

                    // 👉 Wrap each character with a <span> tag
                    barcodeText.innerHTML = barcode.split('').map(char => `<span>${char}</span>`).join('');

                    barcodeImage.onload = function () {
                        adjustTextWidthAndSize();
                    };

                    setTimeout(adjustTextWidthAndSize, 300); // fallback in case onload fails
                } else {
                    alert("Please complete Barcode, Product Name, and Price fields.");
                }
            });



function renderProductList(data = productList) {
    productListContainer.innerHTML = '';

    data.forEach((product, index) => {
        const row = document.createElement('tr');
        row.className = "border-b border-gray-200 hover:bg-gray-100 text-center";

        row.innerHTML = `
            <td class="py-2 px-4">${index + 1}</td>  <!-- Display index + 1 -->
            <td class="py-2 px-4">${product.barcode}</td>
            <td class="py-2 px-4">${product.name}</td>
            <td class="py-2 px-4">₱${product.price}</td>
            <td class="py-2 px-4">
                <div class="flex justify-center space-x-2 mt-1">
                    <button onclick="editProduct(${product.id})" class="bg-yellow-500 text-white px-2 py-1 rounded hover:bg-yellow-600 text-sm">Edit</button>
                    <button onclick="deleteProduct('${product.barcode}')" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 text-sm">Delete</button>
                </div>
            </td>
        `;

        productListContainer.appendChild(row);
    });
}


function adjustTextWidthAndSize() {
     const imageWidth = barcodeImage.offsetWidth;  // Get the width of the barcode image
     const digitCount = barcodeText.innerText.length; // Number of characters in the barcode text
     const fontSize = Math.max(10, imageWidth / (digitCount * 1.3)); // Adjust font size based on barcode width
     const spacing = (imageWidth - digitCount * fontSize) / (digitCount - 1) + 6; // Adjust spacing between characters

     // Adjust the width of barcode text and font size
     barcodeText.style.width = imageWidth + 'px';
     barcodeText.style.fontSize = fontSize + 'px';

     // Adjust the spacing between the barcode text characters
     const spans = barcodeText.getElementsByTagName('span');
     for (let span of spans) {
         span.style.marginRight = `${spacing}px`;
     }

     // Adjust the overlay's width
     overlay.style.width = `${imageWidth}px`;

     // Adjust the position of the overlay relative to the barcode container
     const barcodeContainer = barcodeImage.closest('.barcode-container');
     const containerPadding = parseInt(window.getComputedStyle(barcodeContainer).paddingLeft) || 0; // Get container padding

     // Set the overlay position to align exactly with the barcode width
     overlay.style.left = `${containerPadding}px`;
 }

function loadProductList() {
    fetch('/products')
        .then(response => response.json())
        .then(data => {
            productList = data;
            renderProductList();
        });
}



function deleteProduct(barcode) {
    fetch(`/delete/${barcode}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.status === 204) {
            location.reload();
        } else {
            response.text().then(text => {
                alert('Failed to delete product: ' + text);
            });
        }
    })
    .catch(error => {
        alert('Error deleting: ' + error);
    });
}

searchInput.addEventListener('input', function () {
                const query = searchInput.value.toLowerCase().trim();

     if (query === '') {
         // If search box is empty, show full list
         renderProductList(productList);
         return;
     }

     // Filter products based on exact match of barcode, name, or price
     const filteredProducts = productList.filter(product => {
         const barcodeMatch = product.barcode.toLowerCase() === query;
         const nameMatch = product.name.toLowerCase() === query;
         const priceMatch = product.price.toString() === query;

         return barcodeMatch || nameMatch || priceMatch;
     });

     renderProductList(filteredProducts);
 });

            clearListBtn.addEventListener('click', function () {
                searchInput.value = '';
                renderProductList();
            });

            sortSelect.addEventListener('change', function () {
                const sortBy = sortSelect.value;
                const sortedProducts = [...productList].sort((a, b) => {
                    if (sortBy === 'barcode') return a.barcode.localeCompare(b.barcode);
                    if (sortBy === 'name') return a.name.localeCompare(b.name);
                    if (sortBy === 'price') return a.price - b.price;
                });
                renderProductList(sortedProducts);
            });

            loadProductList(); // Initially load product list when the page is ready
        });




function editProduct(productId) {
    // Fetch product details from the server
    fetch(`/get_product/${productId}`)
        .then(response => response.json())
        .then(product => {
            console.log('Product data:', product); // Debugging line

            if (product.error) {
                alert("Product not found!");
                return;
            }

            // Fill the input fields with the product data
            document.getElementById('barcode').value = product.barcode;
            document.getElementById('name').value = product.name;
            document.getElementById('price').value = product.price;

            // Set the form action to "update"
            const form = document.querySelector('form');
            form.setAttribute('action', `/update/${productId}`);

            // Add method override hidden input if it doesn't exist
            let methodInput = document.querySelector('input[name="_method"]');
            if (!methodInput) {
                methodInput = document.createElement('input');
                methodInput.setAttribute('type', 'hidden');
                methodInput.setAttribute('name', '_method');
                form.appendChild(methodInput);
            }
            methodInput.value = 'PUT';

            // Change button styles for Update
            const updateButton = document.querySelector('button[name="action"][value="update"]');
            updateButton.classList.add('bg-yellow-700');
            updateButton.classList.remove('bg-yellow-500');

            // Show update and cancel buttons, hide the add button
            document.querySelector('[name="action"][value="add"]').classList.add('hidden');
            document.getElementById('update-cancel-buttons').classList.remove('hidden');

            // Cancel button logic
            document.getElementById('cancel-edit').onclick = function () {
                // Clear input fields
                document.getElementById('barcode').value = '';
                document.getElementById('name').value = '';
                document.getElementById('price').value = '';

                // Hide the update and cancel buttons, show the add button
                document.querySelector('[name="action"][value="add"]').classList.remove('hidden');
                document.getElementById('update-cancel-buttons').classList.add('hidden');

                // Remove _method input
                const methodInput = document.querySelector('input[name="_method"]');
                if (methodInput) methodInput.remove();

                // Reset form action back to /add
                form.setAttribute('action', '/add');
            };
        })
        .catch(error => console.error('Error fetching product data:', error));
}




 function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`/delete/${id}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                // Optional: Reload or remove item from DOM
                location.reload();
            } else {
                alert('Failed to delete product.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Something went wrong.');
        });
    }
}

        fetch(`/delete/${id}`, {
    method: 'DELETE',
})
.then(response => {
    if (response.status === 204) {
        location.reload();
    } else {
        return response.text().then(text => {
            alert('Failed to delete: ' + text);
        });
    }
})
.catch(error => {
    console.error('Fetch error:', error);
    alert('Something went wrong.');
});


fetch(`/update/${productId}`, {
    method: 'PUT',  // Ensure it's 'PUT'
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        barcode: document.getElementById('barcode').value,
        name: document.getElementById('name').value,
        price: document.getElementById('price').value
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert("ayos!");
        // You can reload the page or update the UI accordingly
    } else {
        alert(data.error);
    }
})
.catch(error => console.error('Error:', error));

    fetch('/update/1', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    const responseLabel = document.getElementById('response-label');

    if (data.success) {
        responseLabel.textContent = data.message;
        responseLabel.style.color = 'green';
    } else {
        responseLabel.textContent = data.error || "An error occurred.";
        responseLabel.style.color = 'red';

        // Optionally, reset labels or placeholders here too
    }
});

document.getElementById('product-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default submit

    const form = this;
    const action = form.getAttribute('action'); // e.g. /update/18 OR /add
    const methodOverride = form.querySelector('input[name="_method"]');
    const responseLabel = document.getElementById('response-label');
    const formData = new FormData(form);

    // Determine if this is an UPDATE operation
    const isUpdate = methodOverride && methodOverride.value === 'PUT';

    fetch(action, {
        method: 'POST', // Always POST, backend will read _method
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            responseLabel.textContent = data.message;
            responseLabel.style.color = 'green';

            // Reload the product list without full page reload (optional)
            loadProductList();

            // Reset form to default state after update
            if (isUpdate) {
                form.reset();
                document.querySelector('[name="action"][value="add"]').classList.remove('hidden');
                document.getElementById('update-cancel-buttons').classList.add('hidden');

                if (methodOverride) methodOverride.remove();
                form.setAttribute('action', '/add');
            }
        } else {
            responseLabel.textContent = data.error || "May mali sa input.";
            responseLabel.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        responseLabel.textContent = "May error habang nagse-save.";
        responseLabel.style.color = 'red';
    });
});

  function showSuccessMessage(message) {
    const msgDiv = document.getElementById('successMessage');
    msgDiv.innerText = message;
    msgDiv.style.display = 'block';

    setTimeout(() => {
      msgDiv.style.display = 'none';
    }, 3000); // gone after 3 seconds
  }

  // If the server rendered a message (like after POST), show and auto-hide
  const successDiv = document.getElementById('successMessage');
  if (successDiv.innerText.trim() !== '') {
    setTimeout(() => {
      successDiv.style.display = 'none';
    }, 3000);
  }

        const form = document.getElementById('product-form');

form.addEventListener('submit', function (e) {
    const action = e.submitter?.value;
    if (action === 'add' || action === 'update') {
        setTimeout(() => {
            form.reset(); // clear input fields
            document.getElementById('update-cancel-buttons').classList.add('hidden'); // hide update/cancel buttons
        }, 500);
    }
});

form.addEventListener('submit', function (e) {
    const barcode = document.getElementById('barcode');
    const name = document.getElementById('name');
    const price = document.getElementById('price');

    if (!barcode.value.trim() || !name.value.trim() || !price.value.trim()) {
        e.preventDefault();
        alert("Please complete all fields.");
        return false;
    }

    if (Number(price.value) <= 0) {
        e.preventDefault();
        alert("Price must be greater than 0.");
        return false;
    }
});

fetch('/custom_barcode', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    code: '750103131130',
    name: 'Milo 3-in-1',
    price: '12.00'
  })
})
.then(res => res.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
});

  document.getElementById('clear-search').addEventListener('click', function() {
        document.getElementById('search').value = ''; // Clears the search bar
        // Optionally, trigger a function to reload or reset the table
    });

    function validateBarcode(input) {
        // Remove any spaces and check if the input contains only numbers
        input.value = input.value.replace(/\s/g, '');  // Remove spaces
        const regex = /^\d+$/;  // Ensure it's only numbers
        if (!regex.test(input.value)) {
            input.setCustomValidity("Barcode must be numbers only, no spaces.");
        } else {
            input.setCustomValidity("");  // Clear error if valid
        }
    }