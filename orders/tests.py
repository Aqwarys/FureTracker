import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import OrderStatus
from orders.models import Order, Comment, ORDER_NUMBER_ALPHABET, ORDER_NUMBER_LENGTH


class OrderAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = OrderStatus.objects.create(name='Замер', order_index=1)
        cls.private_order = Order.objects.create(
            client_name='Айгерим', client_email='a@example.com', client_phone='+77000000000',
            description='Кухня', order_status=cls.status,
        )
        cls.public_order = Order.objects.create(
            client_name='Ерлан', client_email='e@example.com', client_phone='+77000000001',
            description='Шкаф-купе', order_status=cls.status, is_public=True,
        )
        cls.staff = User.objects.create_user('manager', password='pass', is_staff=True)

    def test_order_number_is_random_and_readable(self):
        number = self.private_order.order_number
        self.assertTrue(number.startswith('ORD-'))
        suffix = number[len('ORD-'):]
        self.assertEqual(len(suffix), ORDER_NUMBER_LENGTH)
        self.assertTrue(all(ch in ORDER_NUMBER_ALPHABET for ch in suffix))
        self.assertNotEqual(self.private_order.order_number, self.public_order.order_number)

    def test_list_shows_only_public_orders_to_visitors(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertContains(response, self.public_order.order_number)
        self.assertNotContains(response, self.private_order.order_number)

    def test_list_shows_all_orders_to_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('orders:order_list'))
        self.assertContains(response, self.public_order.order_number)
        self.assertContains(response, self.private_order.order_number)

    def test_private_order_hidden_by_number(self):
        url = reverse('orders:public_order_detail', args=[self.private_order.order_number])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_private_order_visible_by_number_to_staff(self):
        self.client.force_login(self.staff)
        url = reverse('orders:public_order_detail', args=[self.private_order.order_number])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_public_order_visible_without_comments(self):
        Comment.objects.create(order=self.public_order, author_name='Ерлан', text='Секретная переписка', moderated=True)
        url = reverse('orders:public_order_detail', args=[self.public_order.order_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Секретная переписка')
        self.assertNotContains(response, 'Оставить новый комментарий')

    def test_public_page_rejects_comment_post(self):
        url = reverse('orders:public_order_detail', args=[self.public_order.order_number])
        self.client.post(url, {'author_name': 'Спамер', 'text': 'Реклама'})
        self.assertFalse(Comment.objects.filter(author_name='Спамер').exists())

    def test_client_link_opens_private_order_with_comments(self):
        url = self.private_order.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Оставить новый комментарий')

        response = self.client.post(url, {'author_name': 'Айгерим', 'text': 'Когда замер?'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(order=self.private_order, text='Когда замер?').exists())

    def test_unknown_token_returns_404(self):
        url = reverse('orders:client_order_detail', args=['00000000-0000-0000-0000-000000000000'])
        self.assertEqual(self.client.get(url).status_code, 404)


class UploadApiAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = OrderStatus.objects.create(name='Замер', order_index=1)
        cls.order = Order.objects.create(
            client_name='Айгерим', client_email='a@example.com', client_phone='+77000000000',
            description='Кухня', order_status=cls.status,
        )
        cls.staff = User.objects.create_user('manager', password='pass', is_staff=True)
        cls.customer = User.objects.create_user('customer', password='pass')

    def post_json(self, name, payload):
        return self.client.post(reverse(name), json.dumps(payload), content_type='application/json')

    def test_anonymous_cannot_get_presigned_url(self):
        response = self.post_json('orders:get_s3_presigned_url', {
            'filename': 'a.jpg', 'filetype': 'image/jpeg', 'order_number': self.order.order_number,
        })
        self.assertEqual(response.status_code, 403)

    def test_non_staff_user_cannot_complete_upload(self):
        self.client.force_login(self.customer)
        response = self.post_json('orders:complete_s3_upload', {
            'order_number': self.order.order_number,
            's3_file_path': f'orders/{self.order.order_number}/x.jpg',
            'order_stage_id': self.status.pk,
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.order.media_items.exists())

    def test_staff_cannot_attach_foreign_path(self):
        self.client.force_login(self.staff)
        response = self.post_json('orders:complete_s3_upload', {
            'order_number': self.order.order_number,
            's3_file_path': 'orders/ORD-OTHER/x.jpg',
            'order_stage_id': self.status.pk,
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.order.media_items.exists())


class HealthcheckTests(TestCase):
    def test_healthz(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
