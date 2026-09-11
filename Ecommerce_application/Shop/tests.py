from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Order, OrderItem, Product, Review, Store


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ShopTests(TestCase):
    """Unit tests for the main e-commerce application functionality."""

    def setUp(self):
        self.vendor_group = Group.objects.create(name="Vendor")
        self.buyer_group = Group.objects.create(name="Buyer")
        self.admin_group = Group.objects.create(name="Admin")

        self.vendor = User.objects.create_user(
            username="vendor1",
            email="vendor@example.com",
            password="TestPassword123!",
        )
        self.vendor.groups.add(self.vendor_group)

        self.other_vendor = User.objects.create_user(
            username="vendor2",
            email="vendor2@example.com",
            password="TestPassword123!",
        )
        self.other_vendor.groups.add(self.vendor_group)

        self.buyer = User.objects.create_user(
            username="buyer1",
            email="buyer@example.com",
            password="TestPassword123!",
        )
        self.buyer.groups.add(self.buyer_group)

        self.store = Store.objects.create(
            name="Vendor Store",
            description="A store for testing.",
            vendor=self.vendor,
        )

        self.other_store = Store.objects.create(
            name="Other Store",
            description="Another testing store.",
            vendor=self.other_vendor,
        )

        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal("50.00"),
            description="A product for testing.",
            store=self.store,
        )

        self.other_product = Product.objects.create(
            name="Other Product",
            price=Decimal("25.00"),
            description="Another product for testing.",
            store=self.other_store,
        )

    # -------------------------
    # Authentication and roles
    # -------------------------

    def test_buyer_can_log_in(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "buyer1",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(response, reverse("product_list"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_vendor_is_redirected_to_store_list_after_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "vendor1",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(response, reverse("store_list"))

    def test_registration_creates_buyer(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newbuyer",
                "email": "newbuyer@example.com",
                "password1": "NewPassword123!",
                "password2": "NewPassword123!",
                "role": "Buyer",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="newbuyer")
        self.assertTrue(user.groups.filter(name="Buyer").exists())

    def test_registration_creates_vendor(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newvendor",
                "email": "newvendor@example.com",
                "password1": "NewPassword123!",
                "password2": "NewPassword123!",
                "role": "Vendor",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="newvendor")
        self.assertTrue(user.groups.filter(name="Vendor").exists())

    # -------------------------
    # Product viewing
    # -------------------------

    def test_product_list_is_available(self):
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")

    def test_product_detail_is_available(self):
        response = self.client.get(
            reverse("product_detail", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")
        self.assertContains(response, "50.00")

    # -------------------------
    # Vendor product permissions
    # -------------------------

    def test_vendor_can_create_product(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("product_create"),
            {
                "name": "New Product",
                "price": "75.00",
                "description": "A new product.",
                "store": self.store.id,
            },
        )

        self.assertRedirects(response, reverse("product_list"))
        product = Product.objects.get(name="New Product")
        self.assertEqual(product.store, self.store)
        self.assertEqual(product.price, Decimal("75.00"))

    def test_buyer_cannot_create_product(self):
        self.client.force_login(self.buyer)

        response = self.client.get(reverse("product_create"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), 2)

    def test_vendor_can_edit_own_product(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("product_update", args=[self.product.id]),
            {
                "name": "Updated Product",
                "price": "60.00",
                "description": "Updated description.",
            },
        )

        self.assertRedirects(response, reverse("product_list"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.price, Decimal("60.00"))

    def test_vendor_cannot_edit_another_vendors_product(self):
        self.client.force_login(self.vendor)

        response = self.client.get(
            reverse("product_update", args=[self.other_product.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_buyer_cannot_edit_product(self):
        self.client.force_login(self.buyer)

        response = self.client.get(
            reverse("product_update", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_vendor_can_delete_own_product(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("product_delete", args=[self.product.id])
        )

        self.assertRedirects(response, reverse("product_list"))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_vendor_cannot_delete_another_vendors_product(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("product_delete", args=[self.other_product.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Product.objects.filter(id=self.other_product.id).exists()
        )

    def test_buyer_cannot_delete_product(self):
        self.client.force_login(self.buyer)

        response = self.client.get(
            reverse("product_delete", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())

    # -------------------------
    # Store management
    # -------------------------

    def test_vendor_can_create_store(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("store_create"),
            {
                "name": "New Store",
                "description": "A new store.",
            },
        )

        self.assertRedirects(response, reverse("store_list"))
        store = Store.objects.get(name="New Store")
        self.assertEqual(store.vendor, self.vendor)

    def test_buyer_cannot_create_store(self):
        self.client.force_login(self.buyer)

        response = self.client.get(reverse("store_create"))

        self.assertEqual(response.status_code, 302)

    def test_vendor_can_edit_own_store(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("store.update", args=[self.store.id]),
            {
                "name": "Updated Store",
                "description": "Updated store description.",
            },
        )

        self.assertRedirects(response, reverse("store_list"))
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, "Updated Store")

    def test_vendor_cannot_edit_another_vendors_store(self):
        self.client.force_login(self.vendor)

        response = self.client.get(
            reverse("store.update", args=[self.other_store.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_vendor_can_delete_own_store(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("store_delete", args=[self.store.id])
        )

        self.assertRedirects(response, reverse("store_list"))
        self.assertFalse(Store.objects.filter(id=self.store.id).exists())

    def test_vendor_cannot_delete_another_vendors_store(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("store_delete", args=[self.other_store.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Store.objects.filter(id=self.other_store.id).exists())

    # -------------------------
    # Session shopping cart
    # -------------------------

    def test_logged_in_buyer_can_add_product_to_cart(self):
        self.client.force_login(self.buyer)

        response = self.client.post(
            reverse("add_to_cart", args=[self.product.id]),
            {"quantity": 2},
        )

        self.assertRedirects(response, reverse("cart_detail"))
        self.assertEqual(self.client.session["cart"], {
            str(self.product.id): 2
        })

    def test_adding_same_product_increases_quantity(self):
        self.client.force_login(self.buyer)

        self.client.post(
            reverse("add_to_cart", args=[self.product.id]),
            {"quantity": 2},
        )
        self.client.post(
            reverse("add_to_cart", args=[self.product.id]),
            {"quantity": 3},
        )

        self.assertEqual(
            self.client.session["cart"][str(self.product.id)],
            5,
        )

    def test_buyer_can_remove_product_from_cart(self):
        self.client.force_login(self.buyer)
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()

        response = self.client.get(
            reverse("remove_from_cart", args=[self.product.id])
        )

        self.assertRedirects(response, reverse("cart_detail"))
        self.assertEqual(self.client.session["cart"], {})

    def test_anonymous_user_cannot_access_cart(self):
        response = self.client.get(reverse("cart_detail"))

        self.assertEqual(response.status_code, 302)

    # -------------------------
    # Checkout and invoices
    # -------------------------

    def test_checkout_creates_order_and_order_item(self):
        self.client.force_login(self.buyer)
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()

        response = self.client.post(reverse("checkout"))

        order = Order.objects.get(user=self.buyer)
        order_item = OrderItem.objects.get(order=order)

        self.assertRedirects(
            response,
            reverse("invoice", args=[order.id]),
        )
        self.assertEqual(order.total, Decimal("100.00"))
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("50.00"))

    def test_checkout_clears_session_cart(self):
        self.client.force_login(self.buyer)
        session = self.client.session
        session["cart"] = {str(self.product.id): 1}
        session.save()

        self.client.post(reverse("checkout"))

        self.assertEqual(self.client.session["cart"], {})

    def test_checkout_sends_invoice_email(self):
        self.client.force_login(self.buyer)
        session = self.client.session
        session["cart"] = {str(self.product.id): 1}
        session.save()

        self.client.post(reverse("checkout"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Invoice for Order #", mail.outbox[0].subject)
        self.assertIn("Test Product", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.buyer.email])

    def test_empty_cart_does_not_create_order(self):
        self.client.force_login(self.buyer)

        response = self.client.post(reverse("checkout"))

        self.assertRedirects(response, reverse("cart_detail"))
        self.assertEqual(Order.objects.count(), 0)

    def test_user_can_view_own_invoice(self):
        order = Order.objects.create(
            user=self.buyer,
            total=Decimal("50.00"),
        )

        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse("invoice", args=[order.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_view_another_users_invoice(self):
        order = Order.objects.create(
            user=self.other_vendor,
            total=Decimal("50.00"),
        )

        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse("invoice", args=[order.id])
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------
    # Reviews
    # -------------------------

    def test_buyer_can_leave_unverified_review(self):
        self.client.force_login(self.buyer)

        response = self.client.post(
            reverse("review_create", args=[self.product.id]),
            {
                "rating": 4,
                "comment": "Good product.",
            },
        )

        self.assertRedirects(
            response,
            reverse("product_detail", args=[self.product.id]),
        )
        review = Review.objects.get(user=self.buyer, product=self.product)
        self.assertFalse(review.verified)
        self.assertEqual(review.rating, 4)

    def test_review_is_verified_after_purchase(self):
        order = Order.objects.create(
            user=self.buyer,
            total=Decimal("50.00"),
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )

        self.client.force_login(self.buyer)
        self.client.post(
            reverse("review_create", args=[self.product.id]),
            {
                "rating": 5,
                "comment": "Excellent product.",
            },
        )

        review = Review.objects.get(user=self.buyer, product=self.product)
        self.assertTrue(review.verified)

    def test_anonymous_user_cannot_leave_review(self):
        response = self.client.get(
            reverse("review_create", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)
