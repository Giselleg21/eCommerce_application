# Django eCommerce Application

## Project Description

This project is a Django-based eCommerce web application that allows users to either buy from stores as a **Buyer**, or to create stores and sell items as a **Vendor**.

---

## Features

### User Registration and Authentication

Users can register for an account and log in to the application as either a:

* **Vendor**
* **Buyer**

### Vendor Features

Vendors can:

* Create a store
* View their stores
* Edit their stores
* Remove their stores

Vendors can manage products belonging to their stores. They can:

* Add products
* View products
* Edit products
* Remove products

---

### Buyer Features

Buyers can:

* View products
* View products from different stores
* Add products to their shopping cart
* View their shopping cart
* Checkout their cart
* Receive an invoice by email
* Leave reviews for products

---

## Shopping Cart

The application uses **Django sessions** to keep track of a buyer's shopping cart while they browse the store.

The session-based cart allows products to remain in the buyer's cart as they navigate between different pages of the application.

When the buyer completes the checkout process, the products in the cart are processed and the cart is cleared.

---

## Checkout and Invoices

When a buyer checks out:

1. The products in the buyer's cart are retrieved.
2. The order information is processed.
3. An invoice containing the purchased items is created.
4. The products are removed from the shopping cart.
5. The invoice is sent to the buyer's email address.

This provides the buyer with a record of the products purchased and their associated costs.

---

## Product Reviews

Buyers can leave reviews for products.

Reviews are classified as either **verified** or **unverified**.

### Verified Reviews

A review is considered verified when the buyer has previously purchased the product.

### Unverified Reviews

A buyer can still leave a review for a product that they have not purchased.

These reviews are marked as unverified to distinguish them from reviews written by customers who have purchased the product.

---

## Password Recovery

The application provides functionality for users who have forgotten their passwords.

Users can request a password reset by providing their email address. The application then sends an email containing a password reset URL.

For security, password reset tokens are generated and have an expiry period. This prevents an old password reset URL from being used indefinitely.

---

## Database

The application uses a **relational database** as its backend.

Django's migration system is used to create and maintain the database structure.

The main database-related commands used during development include:

```bash
python manage.py makemigrations
python manage.py migrate
```

These commands create migration files based on changes to the Django models and apply those migrations to the database.

---

## Technologies Used

* Python
* Django
* HTML
* CSS
* Relational Database
* Django Sessions
* Django Authentication
* Email functionality
* Django ORM

---

## Project Structure

The project follows the standard Django project structure.

```text
Ecommerce_Project/
│
├── Ecommerce_application/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── Shop/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── manage.py
├── db.sqlite3
└── README.md
```

> **Note:** The exact files and folders may vary depending on the implementation of the application.
