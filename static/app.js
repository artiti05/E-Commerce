document.addEventListener('DOMContentLoaded', () => {
    const customerSelect = document.getElementById('customer-select');
    const productsGrid = document.getElementById('products-grid');
    const cartItemsList = document.getElementById('cart-items-list');
    const cartItemCount = document.getElementById('cart-item-count');
    const cartTotalPrice = document.getElementById('cart-total-price');
    const consoleLogs = document.getElementById('console-logs');
    const toastContainer = document.getElementById('toast-container');
    const checkoutBtn = document.getElementById('checkout-btn');

    let currentCustomerId = parseInt(customerSelect.value);
    let logOffset = 0; // tracks how many log lines we have parsed

    // ==========================================
    // Core Functions
    // ==========================================

    // Fetch and render the store catalog
    async function loadProducts() {
        try {
            const response = await fetch('/api/products');
            const products = await response.json();
            
            productsGrid.innerHTML = '';
            products.forEach(product => {
                const stockStatus = product.qty > 5 ? 'In Stock' : (product.qty > 0 ? 'Low Stock' : 'Out of Stock');
                const badgeClass = product.qty > 5 ? 'in-stock' : (product.qty > 0 ? 'low-stock' : 'out-of-stock');
                const icon = product.qty > 5 ? 'circle-check' : (product.qty > 0 ? 'triangle-exclamation' : 'circle-xmark');
                
                // Map local generated images
                let imagePath = 'images/laptop.png';
                if (product.name.toLowerCase().includes('mouse')) imagePath = 'images/mouse.png';
                else if (product.name.toLowerCase().includes('keyboard')) imagePath = 'images/keyboard.png';

                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <div class="image-container">
                        <img src="${imagePath}" alt="${product.name}" class="product-image">
                        <span class="stock-badge ${badgeClass}">
                            <i class="fa-solid fa-${icon}"></i> ${stockStatus}
                        </span>
                    </div>
                    <div class="product-info">
                        <h3 class="product-name">${product.name}</h3>
                        <div class="product-pricing">
                            <span class="product-price">$${parseFloat(product.price).toFixed(2)}</span>
                            <span class="product-stock-text">${product.qty} left in stock</span>
                        </div>
                        <div class="action-row">
                            <input type="number" id="qty-${product.id}" class="qty-input" value="1" min="1" max="${product.qty}" ${product.qty === 0 ? 'disabled' : ''}>
                            <button class="add-to-cart-btn" data-id="${product.id}" ${product.qty === 0 ? 'disabled' : ''}>
                                <i class="fa-solid fa-cart-plus"></i> Add
                            </button>
                        </div>
                    </div>
                `;
                productsGrid.appendChild(card);
            });

            // Re-bind click event handlers for the newly rendered buttons
            document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
                btn.addEventListener('click', handleAddToCart);
            });
        } catch (error) {
            console.error('Error loading products:', error);
            showToast('Failed to load store products.');
        }
    }

    // Fetch and render the customer's cart
    async function loadCart() {
        try {
            const response = await fetch(`/api/cart/${currentCustomerId}`);
            const cart = await response.json();
            
            cartItemsList.innerHTML = '';
            
            if (!cart.items || cart.items.length === 0) {
                cartItemsList.innerHTML = `
                    <div class="empty-cart-state">
                        <i class="fa-solid fa-basket-shopping empty-icon"></i>
                        <p>Your cart is empty. Add products to get started.</p>
                    </div>
                `;
                cartItemCount.textContent = '0';
                cartTotalPrice.textContent = '$0.00';
                return;
            }

            let totalQty = 0;
            cart.items.forEach(item => {
                totalQty += item.qty;
                const subtotal = parseFloat(item.product.price) * item.qty;
                
                const itemDiv = document.createElement('div');
                itemDiv.className = 'cart-item';
                itemDiv.innerHTML = `
                    <div class="item-details">
                        <span class="item-name">${item.product.name}</span>
                        <span class="item-price">$${parseFloat(item.product.price).toFixed(2)} x ${item.qty}</span>
                    </div>
                    <span class="item-subtotal">$${subtotal.toFixed(2)}</span>
                    <button class="item-remove-btn" data-id="${item.product.id}">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                `;
                cartItemsList.appendChild(itemDiv);
            });

            cartItemCount.textContent = totalQty;
            cartTotalPrice.textContent = `$${parseFloat(cart.total_price).toFixed(2)}`;

            // Bind click handlers for delete buttons
            document.querySelectorAll('.item-remove-btn').forEach(btn => {
                btn.addEventListener('click', handleRemoveFromCart);
            });
        } catch (error) {
            console.error('Error loading cart:', error);
            showToast('Failed to fetch shopping cart state.');
        }
    }

    // Add item click event handler
    async function handleAddToCart(e) {
        const btn = e.currentTarget;
        const productId = parseInt(btn.getAttribute('data-id'));
        const qtyInput = document.getElementById(`qty-${productId}`);
        const qty = parseInt(qtyInput.value);

        if (isNaN(qty) || qty <= 0) {
            showToast('Please enter a valid quantity.');
            return;
        }

        try {
            const response = await fetch('/api/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: currentCustomerId,
                    product_id: productId,
                    qty: qty
                })
            });

            const data = await response.json();
            if (!response.ok) {
                showToast(data.detail || 'Failed to add item to cart.');
            } else {
                // Reload data
                await loadCart();
                await loadProducts(); // Update stock inventory numbers on catalog cards
            }
        } catch (error) {
            console.error('Error adding item to cart:', error);
            showToast('Network error while adding item.');
        }
    }

    // Remove item click event handler
    async function handleRemoveFromCart(e) {
        const btn = e.currentTarget;
        const productId = parseInt(btn.getAttribute('data-id'));

        try {
            const response = await fetch('/api/cart/remove', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: currentCustomerId,
                    product_id: productId
                })
            });

            const data = await response.json();
            if (!response.ok) {
                showToast(data.detail || 'Failed to remove item.');
            } else {
                // Reload data
                await loadCart();
                await loadProducts(); // Re-read inventory count
            }
        } catch (error) {
            console.error('Error removing item from cart:', error);
            showToast('Network error while removing item.');
        }
    }

    // Switch Customer ID handler
    customerSelect.addEventListener('change', () => {
        currentCustomerId = parseInt(customerSelect.value);
        loadCart();
        showToast(`Switched workspace session to Customer #${currentCustomerId}`, 'info');
    });

    // Dummy Checkout handler
    checkoutBtn.addEventListener('click', () => {
        if (cartItemCount.textContent === '0') {
            showToast('Your cart is empty.');
            return;
        }
        showToast(`Checkout simulated successfully for Customer #${currentCustomerId}!`, 'success');
    });

    // ==========================================
    // Real-time Logger Terminal
    // ==========================================
    async function streamLogs() {
        try {
            const response = await fetch(`/api/logs?offset=${logOffset}`);
            const data = await response.json();
            
            if (data.lines && data.lines.length > 0) {
                if (logOffset === 0) {
                    consoleLogs.innerHTML = ''; // clear waiting placeholder
                }
                
                data.lines.forEach(line => {
                    const logDiv = document.createElement('div');
                    logDiv.className = 'log-entry';
                    
                    // Style log levels
                    if (line.includes('[INFO]')) logDiv.classList.add('log-info');
                    else if (line.includes('[DEBUG]')) logDiv.classList.add('log-debug');
                    else if (line.includes('[WARNING]')) logDiv.classList.add('log-warning');
                    else if (line.includes('[ERROR]')) logDiv.classList.add('log-error');
                    
                    logDiv.textContent = line;
                    consoleLogs.appendChild(logDiv);
                });
                
                logOffset = data.new_offset;
                consoleLogs.scrollTop = consoleLogs.scrollHeight; // Auto Scroll
            }
        } catch (error) {
            console.error('Error reading application log stream:', error);
        }
    }

    // ==========================================
    // Toast Notification helper
    // ==========================================
    function showToast(message, type = 'error') {
        const toast = document.createElement('div');
        toast.className = 'toast';
        if (type === 'success') {
            toast.style.background = 'rgba(16, 185, 129, 0.95)';
            toast.style.borderLeft = '4px solid #047857';
        } else if (type === 'info') {
            toast.style.background = 'rgba(59, 130, 246, 0.95)';
            toast.style.borderLeft = '4px solid #1d4ed8';
        }
        toast.textContent = message;
        toastContainer.appendChild(toast);
        
        // Remove toast automatically
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    // ==========================================
    // Init Calls
    // ==========================================
    loadProducts();
    loadCart();
    
    // Poll logs every 1.5 seconds
    setInterval(streamLogs, 1500);
});
