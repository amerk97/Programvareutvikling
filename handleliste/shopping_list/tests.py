from django.test import TestCase, Client
from django.urls import reverse
from .models import Item, ShoppingList
from django.contrib.auth import get_user_model
from .views import *

User = get_user_model()


# Create your tests here.
class ShoppingListViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='testowner', password='12345testing')
        self.participants_en = User.objects.create_user(username = 'testparticipant1', password='12345testing')
        self.participants_to = User.objects.create_user(username='testparticipant2', password='12345testing')
        self.admin = User.objects.create_user(username = 'testadmin1', password = '12345testing');

        self.client.login(username='testowner', password='12345testing')

        self.detail_shopping_list_url = reverse('detail', args='1')
        self.share_shopping_list_url = reverse('share-shopping-list', args='1')

        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )

        # Create a list for test_delete_list:
        self.detail_shopping_list_url_2 = reverse('detail', args='2')
        self.share_shopping_list_url_2 = reverse('share-shopping-list', args='2')

        self.shopping_list_2 = ShoppingList.objects.create(
            title='TestSletteListe',
            owner=self.owner
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

    def test_share_shopping_list_POST(self):
        response1 = self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })

        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, self.detail_shopping_list_url)

        response2 = self.client.post(self.share_shopping_list_url, {
            'username': self.participants_to
        })

        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, self.detail_shopping_list_url)

        response3 = self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        self.assertEqual(response3.status_code, 302)
        self.assertRedirects(response3, self.detail_shopping_list_url)

        # Check that none of the users are in participants, check that self.owner is owner:
        bool_users_not_admin = (self.participants_en and self.participants_to) not in self.shopping_list.admins.all()
        self.assertTrue(bool_users_not_admin)

        bool_users_participants = (self.participants_en and self.participants_to) in self.shopping_list.participants.all()
        self.assertTrue(bool_users_participants)

        bool_owner = self.owner == self.shopping_list.owner
        self.assertTrue(bool_owner)

    def test_make_user_admin_of_shopping_list_POST(self):
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_to
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })

        self.make_user_admin_of_shopping_list_url_1 = reverse('make-admin', args=['1', self.admin])
        response = self.client.post(self.make_user_admin_of_shopping_list_url_1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)

        self.make_user_admin_of_shopping_list_url_2 = reverse('make-admin', args=['1', self.participants_to])
        response = self.client.post(self.make_user_admin_of_shopping_list_url_2)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Check is user who is made admin is in admin-list for the shopping list:
        bool_admin_i_adminliste = (self.admin in self.shopping_list.admins.all()) and (self.admin not in self.shopping_list.participants.all())
        self.assertTrue(bool_admin_i_adminliste)

    def test_remove_user_from_list_POST(self):
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_to
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })

        self.remove_user_from_list_url = reverse('remove-user-from-shopping-list', args=['1', self.participants_en])
        response_remove = self.client.post(self.remove_user_from_list_url)
        self.assertEqual(response_remove.status_code, 302)
        self.assertRedirects(response_remove, self.detail_shopping_list_url)

        # Check if user "participants_en" still is in participants-list for the shopping-list:
        bool_is_removed = (self.participants_en not in self.shopping_list.participants.all()) and (self.shopping_list not in get_user_shopping_lists(self.participants_en))
        self.assertTrue(bool_is_removed)

    def test_delete_shopping_list_POST(self):
        # Check if user "self.owner' is owner of shopping_list_2_
        check_owner = self.owner == self.shopping_list.owner
        self.assertTrue(check_owner)

        # Delete list and check status_code:
        self.index_url = reverse('index')
        self.delete_shopping_list_url = reverse('delete-shopping-list', args='2')
        response_delete_list = self.client.post(self.delete_shopping_list_url, {
            'username': self.owner.username
        })
        self.assertEqual(response_delete_list.status_code, 302)
        self.assertRedirects(response_delete_list, self.index_url)

        shopping_list_is_deleted = self.shopping_list_2 not in get_user_shopping_lists(self.owner)
        self.assertTrue(shopping_list_is_deleted)
