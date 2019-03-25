from django.test import TestCase, Client
from django.urls import reverse
from .models import Item, ShoppingList
from django.contrib.auth import get_user_model
from .views import *

User = get_user_model()


# Create your tests here.
class ShoppingListViews(TestCase):

    def setUp(self):
        #making users that can be used in tests
        self.owner = User.objects.create_user(username='testowner', password='12345testing')
        self.participants_en = User.objects.create_user(username = 'testparticipant1', password='12345testing')
        self.participants_to = User.objects.create_user(username='testparticipant2', password='12345testing')
        self.admin = User.objects.create_user(username = 'testadmin1', password = '12345testing');
        #making a client, and owner logs in
        self.client = Client()
        self.client.login(username='testowner', password='12345testing')
        #making urls to shopping list used in tests
        self.detail_shopping_list_url = reverse('detail', args='1')
        self.share_shopping_list_url = reverse('share-shopping-list', args='1')
        # Don't think we need this
        # self.detail_shopping_list_url_2 = reverse('detail', args='2')
        # self.share_shopping_list_url_2 = reverse('share-shopping-list', args='2')
        #makes two test lists
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        self.shopping_list_2 = ShoppingList.objects.create(
            title='TestSletteListe',
            owner=self.owner
        )
        comment_content = 'What a cool shoppinglist, and what a page! But can handle comments?'
        self.comment = Comment.objects.create(
            author = self.owner,
            content = comment_content,
            shopping_list = self.shopping_list
        )
        reply_comment = 'Well of course you can'
        self.reply_comment = Comment.objects.create(
            author = self.participants_to,
            content = reply_comment,
            shopping_list = self.shopping_list
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
        response = self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })
        response2 = self.client.post(self.share_shopping_list_url, {
            'username': self.participants_to
        })
        response3 = self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        #tests that list is shared with participant one
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
        # tests that list is shared with participant two
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, self.detail_shopping_list_url)
        # tests that list is shared with participant three
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
        #makes self.admin a partcipant of teh list
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
        bool_is_removed = (self.participants_en not in self.shopping_list.participants.all()) and (self.shopping_list not in ShoppingList.get_user_shopping_lists(self.participants_en))
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

        shopping_list_is_deleted = self.shopping_list_2 not in ShoppingList.get_user_shopping_lists(self.owner)
        self.assertTrue(shopping_list_is_deleted)

    def test_admin_leaves_list_POST(self):
        #Adds user as particpant
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        #makes user admin
        self.make_user_admin_of_shopping_list_url = reverse('make-admin', args=['1', self.admin])
        self.client.post(self.make_user_admin_of_shopping_list_url)
        #Admin leaves list
        self.remove_user_from_list_url = reverse('remove-user-from-shopping-list', args=['1', self.admin])
        response_remove = self.client.post(self.remove_user_from_list_url)
        #Test if admin has left the shoppinglist
        self.assertEqual(response_remove.status_code, 302)
        self.assertRedirects(response_remove, self.detail_shopping_list_url)
        bool_is_removed = (self.admin not in self.shopping_list.participants.all()) and (
                    self.shopping_list not in ShoppingList.get_user_shopping_lists(self.admin))
        self.assertTrue(bool_is_removed)

    def test_owner_leaves_list_POST(self):
        # Adds user as particpant
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        # makes user admin
        self.make_user_admin_of_shopping_list_url = reverse('make-admin', args=['1', self.admin])
        self.client.post(self.make_user_admin_of_shopping_list_url)
        #make admin owner
        self.change_owner_of_shopping_list_url = reverse('change-owner', args=['1', self.admin])
        response_change_owner = self.client.post(self.change_owner_of_shopping_list_url)
        # assert tests of change owner
        self.assertEquals(response_change_owner.status_code, 302)
        self.index_url = reverse('index')
        self.assertRedirects(response_change_owner, self.index_url)
        #testing if change owner suceeded
        bool_owner_is_removed = (self.shopping_list not in get_user_shopping_lists(self.owner)) and (self.shopping_list not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list in get_user_shopping_lists(self.admin)) and (self.shopping_list in ShoppingList.objects.filter(owner=self.admin)) and (self.admin not in self.shopping_list.admins.all())
        self.assertTrue(bool_owner_is_removed)
        self.assertTrue(bool_admin_is_owner)

    def test_add_comment_POST(self):
        #add a comment on a shoppinglist

        self.add_comment_url = reverse('add-comment', args = '1')
        response = self.client.post(self.add_comment_url, {
            'author': self.owner,                                                 #FJERNE??
            'content': comment_content,
            'shopping_list': self.shopping_list                                   #FJERNE??
        })
        #testing if comment is added
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
        #ShoppingList.get_user_shopping_lists(self.admin)
        bool_comment_is_added = Comment
        self.assertTrue(bool_comment_is_added)

    def test_delete_comment_POST(self):
        #make a comment
        comment_content = 'And ditch them?'
        self.client.post(self.add_comment_url, {
            'author': self.owner,                                                 #FJERNE??
            'content': comment_content,
            'shopping_list': self.shopping_list                                   #FJERNE??
        })
        #delete the comment
        self.delete_comment_url = reverse('delete-comment', args = ['1', '1'])
        response = self.client.post(self.delete_comment_url)
        #tests if comment is deleted
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
        #bool_comment_is_removed =
        self.assertTrue(bool_comment_is_removed)

    def test_reply_comment_POST(self):
        # make a comment
        comment_content = 'And ditch them?'
        self.client.post(self.add_comment_url, {
            'author': self.owner,  # FJERNE??
            'content': comment_content,
            'shopping_list': self.shopping_list  # FJERNE??
        })
        #reply to the comment

        self.reply_comment_url = reverse('reply', args = ['1','1'])
        response = self.client.post(self.reply_comment_url)
        #test if comment is replied
        self.assertEquals(response.status_code, 302)
        self.asserRedirects(response, self.detail_shopping_list_url)
        #bool_comment_is_replied =
        self.assertTrue(bool_comment_is_replied)