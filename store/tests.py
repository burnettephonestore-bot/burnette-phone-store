from django.test import TestCase
from django.urls import reverse
from .models import Product, Cart, Request
from django.contrib.auth.models import User


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Phone",
            price=1000000.00,
            description="A test smartphone"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Phone")
        self.assertEqual(self.product.price, 1000000.00)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.product = Product.objects.create(
            name="Test Phone",
            price=1000000.00,
            description="A test smartphone"
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )

    def test_cart_total_price(self):
        expected_total = self.product.price * self.cart_item.quantity
        self.assertEqual(self.cart_item.total_price, expected_total)


class ViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.product = Product.objects.create(
            name="Test Phone",
            price=1000000.00,
            description="A test smartphone"
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Burnette Phone Store")

    def test_products_view(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Phone")

    def test_login_required_cart(self):
        response = self.client.get(reverse('view_cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_request_submission_and_history(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.post(reverse('request_product'), {
            'product': self.product.id,
            'name': 'Test User',
            'phone': '0712345678',
            'email': 'testuser@example.com',
            'discount': '0',
            'wants_delivery': 'false',
            'payment_method': 'bank',
            'bank_name': 'Test Bank',
        })
        self.assertEqual(response.status_code, 302)

        # Ensure the request was created
        self.assertEqual(Request.objects.count(), 1)
        req = Request.objects.first()
        self.assertEqual(req.product_name, 'Test Phone')
        self.assertEqual(req.contact_name, 'Test User')
        self.assertEqual(req.user, self.user)

        # The view should persist the provided phone to the user profile
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.phone, '0712345678')

        # Create a request for another user to ensure history isolation
        other_user = User.objects.create_user(username='otheruser', password='12345', email='other@example.com')
        Request.objects.create(
            user=other_user,
            product=self.product,
            product_name=self.product.name,
            base_price=self.product.price,
            discount=0,
            final_price=self.product.price,
            explanation='Other user request',
            contact_name='Other User',
            contact_phone='0700000000',
            contact_email='other@example.com',
            wants_delivery=False,
        )

        response = self.client.get(reverse('request_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Phone')
        self.assertContains(response, 'Test User')
        self.assertNotContains(response, 'Other User')

        # Legacy requests that existed before the `user` field was added should still appear.
        Request.objects.create(
            user=None,
            product=self.product,
            product_name=self.product.name,
            base_price=self.product.price,
            discount=0,
            final_price=self.product.price,
            explanation='Legacy request by email',
            contact_name='Test User',
            contact_phone='0712345678',
            contact_email='testuser@example.com',
            wants_delivery=False,
        )

        response = self.client.get(reverse('request_history'))
        self.assertContains(response, 'testuser@example.com')