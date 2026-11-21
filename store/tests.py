from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from decimal import Decimal

from .models import Product, Order, OrderItem


class StorePageTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Trail Mug',
            description='A durable everyday mug.',
            price='24.50',
            stock=2,
        )

    def test_product_detail_uses_the_product_template(self):
        self.client.force_login(
            User.objects.create_user(username='shopper', password='test-password')
        )
        response = self.client.get(
            reverse('product_detail', args=[self.product.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trail Mug')
        self.assertContains(response, 'Add to cart')
        self.assertNotContains(response, 'Product Form')

    def test_custom_not_found_page_is_rendered(self):
        with override_settings(DEBUG=False):
            response = self.client.get('/this-page-does-not-exist/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "We couldn't find that page", status_code=404)

    def test_home_page_search_and_sorting(self):
        Product.objects.create(name='Leather Bag', description='Crafted leather.', price='89.00', stock=5)
        Product.objects.create(name='Ceramic Cup', description='Minimalist cup.', price='15.00', stock=0)

        # Search
        res = self.client.get(reverse('home'), {'q': 'Leather'})
        self.assertContains(res, 'Leather Bag')
        self.assertNotContains(res, 'Trail Mug')

        # Stock filter
        res_stock = self.client.get(reverse('home'), {'stock': 'in_stock'})
        self.assertContains(res_stock, 'Leather Bag')
        self.assertContains(res_stock, 'Trail Mug')
        self.assertNotContains(res_stock, 'Ceramic Cup')

        # Price sorting
        res_sort = self.client.get(reverse('home'), {'sort': 'price_asc'})
        self.assertEqual(res_sort.status_code, 200)


class StoreActionTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Trail Mug',
            description='A durable everyday mug.',
            price='24.50',
            stock=3,
        )
        self.customer = User.objects.create_user(
            username='customer',
            password='test-password',
        )

    def test_add_to_cart_adds_item_and_respects_stock(self):
        # Set stock to 1 for this test
        self.product.stock = 1
        self.product.save()

        self.client.force_login(self.customer)
        url = reverse('add_to_cart', args=[self.product.id])

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 1})

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 1})
        self.assertContains(response, 'out of stock')

    def test_update_cart_quantity(self):
        self.client.force_login(self.customer)
        # Add to cart first
        self.client.post(reverse('add_to_cart', args=[self.product.id]))

        # Increase
        self.client.post(reverse('update_cart', args=[self.product.id]), {'action': 'increase'})
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 2)

        # Decrease
        self.client.post(reverse('update_cart', args=[self.product.id]), {'action': 'decrease'})
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 1)

    def test_checkout_and_orders_flow(self):
        self.client.force_login(self.customer)
        self.client.post(reverse('add_to_cart', args=[self.product.id]))

        # View cart
        res_cart = self.client.get(reverse('view_cart'))
        self.assertContains(res_cart, 'Trail Mug')
        self.assertContains(res_cart, 'Proceed to checkout')

        # Get checkout page
        res_checkout = self.client.get(reverse('checkout'))
        self.assertContains(res_checkout, 'Delivery Address')
        self.assertContains(res_checkout, 'Place Order')

        # Post checkout
        res_order = self.client.post(reverse('checkout'), {
            'address': '123 Baker Street, Apartment 4B, London'
        }, follow=True)
        self.assertContains(res_order, 'Order placed successfully')
        self.assertEqual(Order.objects.filter(user=self.customer).count(), 1)

        # Check orders view
        res_orders = self.client.get(reverse('my_orders'))
        self.assertContains(res_orders, 'Order #')
        self.assertContains(res_orders, 'Trail Mug')

    def test_staff_can_add_update_and_delete_products(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.get(reverse('add_product'))
        self.assertContains(response, 'Add a product')

        response = self.client.post(reverse('add_product'), {
            'name': 'Desk Lamp',
            'description': 'Warm reading light.',
            'price': '39.99',
            'stock': 3,
            'image': '',
        })
        self.assertRedirects(response, reverse('home'))
        new_product = Product.objects.get(name='Desk Lamp')

        response = self.client.post(
            reverse('update_product', args=[new_product.id]),
            {
                'name': 'Desk Lamp Pro',
                'description': 'Updated reading light.',
                'price': '44.99',
                'stock': 4,
                'image': '',
            },
        )
        self.assertRedirects(response, reverse('home'))
        new_product.refresh_from_db()
        self.assertEqual(new_product.name, 'Desk Lamp Pro')

        response = self.client.get(
            reverse('delete_product', args=[new_product.id])
        )
        self.assertContains(response, 'Yes, delete product')
        response = self.client.post(
            reverse('delete_product', args=[new_product.id])
        )
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Product.objects.filter(pk=new_product.id).exists())

    def test_navigation_logs_out_with_post(self):
        self.client.force_login(self.customer)

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'action="{}"'.format(reverse('logout')))

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
