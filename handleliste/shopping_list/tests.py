from django.test import TestCase, Client
from django.urls import reverse
from .models import Item, ShoppingList
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
class ShoppingListViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        self.detail_shopping_list_url = reverse('detail', args='1')
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.user
        )

    def test_detail_shopping_list_GET(self):
        response = self.client.post(self.detail_shopping_list_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shoppinglist.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list)

    def test_add_item_POST(self):
        add_url = reverse('add', args='1')
        item_name = 'Sjokolade'
        item_amount = '1 stk'
        response = self.client.post(add_url, {
            'name': item_name,
            'amount': item_amount
            }
        )
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
