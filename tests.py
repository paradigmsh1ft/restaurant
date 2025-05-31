from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from restaurant.models import MenuItem, Order, Invoice

class RestaurantAPITests(APITestCase):
    def setUp(self):
        # Створюємо користувачів
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.client_user = User.objects.create_user(username='client', password='clientpass')

        # Створюємо меню
        self.menu_item = MenuItem.objects.create(name="Pizza", price=100.00, category="Main")

        # Ініціалізуємо APIClient без логіну
        self.admin_client = APIClient()
        self.client_client = APIClient()

        # Генеруємо JWT токени для admin і додаємо в заголовок Authorization
        admin_refresh = RefreshToken.for_user(self.admin_user)
        admin_access_token = str(admin_refresh.access_token)
        self.admin_client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_access_token)

        # Генеруємо JWT токени для client і додаємо в заголовок Authorization
        client_refresh = RefreshToken.for_user(self.client_user)
        client_access_token = str(client_refresh.access_token)
        self.client_client.credentials(HTTP_AUTHORIZATION='Bearer ' + client_access_token)

    def test_client_creates_order(self):
        url = '/api/orders/'
        data = {
            "customer_name": "Ivan",
            "items": [{"menu_item": self.menu_item.id, "quantity": 2}]
        }
        response = self.client_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], "Ivan")

    def test_admin_confirms_order(self):
        order = Order.objects.create(customer_name='Ivan')
        url = f'/api/orders/{order.id}/confirm/'
        response = self.admin_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')

    def test_client_cannot_confirm_order(self):
        order = Order.objects.create(customer_name='Ivan')
        url = f'/api/orders/{order.id}/confirm/'
        response = self.client_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_creates_invoice_and_client_pays(self):
        order = Order.objects.create(customer_name='Ivan', status='completed')
        invoice = Invoice.objects.create(order=order, total_amount=200.00)

        url = f'/api/invoices/{invoice.id}/pay/'
        response = self.client_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invoice.refresh_from_db()
        self.assertTrue(invoice.paid)
