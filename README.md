# ✦ Northstar — Full-Stack Django E-Commerce Platform

A modern, responsive full-stack e-commerce web application built with **Django**, featuring a curated minimalist storefront, session-based shopping cart, atomic checkout with Cash on Delivery (COD), order tracking dashboard, and staff inventory management.

---

## 📸 Key Features

- **🛍️ Curated Storefront & Catalog**:
  - Emerald & Slate design system with fluid typography (`Plus Jakarta Sans` & `Space Grotesk`).
  - Hero promotional banner and trust badges (Express Delivery, Authentic Quality, Easy Returns).
  - Search bar with instant query clear, live stock filtering (*In Stock Only*), and multi-criteria sorting (*Newest*, *Price: Low to High*, *Price: High to Low*).
  - Product cards featuring hover zoom, animated stock status pills, and direct "Add to Cart".

- **🔍 Rich Product Details**:
  - High-resolution image showcase with graceful fallback placeholders.
  - Interactive quantity picker with real-time stock limits.
  - "You Might Also Like" related product recommendations carousel.
  - Staff management controls (quick Edit & Delete shortcuts).

- **🛒 Interactive Shopping Bag**:
  - Real-time navbar cart badge counter powered by a custom Django context processor.
  - Live quantity adjustment (`+` and `−`) and remove actions directly in the cart view.
  - Sticky Order Summary sidebar with tax/shipping breakdown and checkout CTA.

- **💳 Streamlined Checkout**:
  - Two-column checkout flow with delivery address validation.
  - Cash on Delivery (COD) payment method with order security verification.
  - Sticky order item preview and grand total breakdown.
  - Atomic database transactions with row-level locking (`select_for_update`) to prevent overselling.

- **📦 Customer Order History Dashboard**:
  - Order tracking with color-coded status badges (`Pending`, `Delivered`, `Completed`).
  - Itemized product purchase table with thumbnails, unit prices, and quantities.
  - Destination shipping address review.

- **🛡️ Staff & Catalog Management**:
  - Form for adding and updating products with price, stock, description, and image URL.
  - Safe deletion confirmation flow with product preview card.

- **🔐 User Authentication**:
  - User registration and login views with form validation.
  - Secure POST-only session logout.

---

## 🏗️ Project Architecture

```
Django_FSD_E-com_Project_Rajees_20112026/
├── ecommerce/                   # Django Project Root
│   ├── __init__.py              # Python 3.14 compatibility layer
│   ├── asgi.py
│   ├── settings.py              # Configuration, context processors, auth
│   ├── urls.py                  # Root URL configuration & 404 handler
│   └── wsgi.py
├── store/                       # Main Store Application
│   ├── migrations/              # Database schema migrations
│   ├── templates/               # HTML5 templates
│   │   ├── base.html            # Global theme layout, navbar, toasts, footer
│   │   ├── home.html            # Storefront catalog, hero, search, filters
│   │   ├── product_detail.html  # Product showcase & related recommendations
│   │   ├── cart.html            # Shopping cart with quantity adjustment
│   │   ├── checkout.html        # Checkout & address submission
│   │   ├── orders.html          # Order tracking dashboard
│   │   ├── product_form.html    # Staff add / edit product editor
│   │   ├── delete_product.html  # Staff product deletion confirmation
│   │   ├── login.html           # Authentication login card
│   │   ├── register.html        # User account registration card
│   │   └── 404.html             # Custom branded error page
│   ├── admin.py                 # Django admin registration
│   ├── apps.py                  # App configuration
│   ├── context_processors.py    # Global cart item counter
│   ├── forms.py                 # Product & Checkout forms
│   ├── models.py                # Product, Order, OrderItem models
│   ├── tests.py                 # Automated test suite (8 comprehensive tests)
│   ├── urls.py                  # Store routing endpoints
│   └── views.py                 # Business logic, cart & order handlers
├── db.sqlite3                   # SQLite database (pre-seeded with demo catalog)
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13, 3.14)
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/ObsidionVortex/FSD.git
cd FSD
```

### 3. Create & Activate Virtual Environment
**On Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Run the Test Suite
```bash
python manage.py test
```
All 8 automated tests should pass:
```
Ran 8 tests in 0.600s
OK
```

### 7. Start the Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🧪 Test Suite Coverage

The test suite in `store/tests.py` validates:
1. Product detail view rendering and templates.
2. Custom 404 page handling.
3. Cart addition, session persistence, and inventory stock limitation enforcement.
4. Cart quantity increments and decrements via `update_cart`.
5. Atomic checkout transactions, stock deduction, and order placement.
6. Order history retrieval and rendering in `my_orders`.
7. Staff permissions for adding, updating, and deleting products.
8. Secure POST logout navigation flow.

---

## 📄 License
This project was developed for educational and Full-Stack Web Development (FSD) demonstration purposes.
