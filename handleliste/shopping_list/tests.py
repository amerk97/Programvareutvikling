from django.test import TestCase

from .models import Item, ShoppingList
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your tests here.


class ItemModelTests(TestCase):
    user = None

    def create_user(self):
        self.credentials = {
            'username': 'testTest',
            'password': '1ab2bgewr1t3'
        }
        # tests login and creates a test user
        self.user = User.objects.create_user(**self.credentials)
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)

    def test_added_item_is_not_bought(self):
        shopping_list = ShoppingList(
            title='Desert',
            owner=self.user
        )
        item = Item(
            name='Sjokolade',
            amount='10 stk',
            shopping_list=shopping_list,
            creator=self.user
        )
        self.assertFalse(item.bought)
