from django.test import TestCase

from .models import Item, ShoppingList
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your tests here.


class ItemMethodTests(TestCase):
    self.user = User.objects.create_user(username='testuser', password='12345')
    login = self.client.login(username='testuser', password='12345')

    def added_item_is_not_bought(self):
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
