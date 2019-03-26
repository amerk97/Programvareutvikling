from django.test import TestCase, Client
from django.urls import reverse
from .models import Item, ShoppingList, Comment, Reply
from django.contrib.auth import get_user_model
from .views import *

User = get_user_model()


# Create your tests here.
class ShoppingListViews(TestCase):

    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(username='testowner', password='12345testing')
        self.participants_en = User.objects.create_user(username='testparticipant1', password='12345testing')
        self.participants_to = User.objects.create_user(username='testparticipant2', password='12345testing')
        self.admin = User.objects.create_user(username='testadmin1', password='12345testing')
        # Create client and log in with owner
        self.client = Client()
        self.client.login(username='testowner', password='12345testing')
        # Shopping list urls
        self.detail_shopping_list_url = reverse('detail', args='1')
        self.share_shopping_list_url = reverse('share-shopping-list', args='1')
        self.index_url = reverse('index')
        # Create shopping lists
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        self.shopping_list_2 = ShoppingList.objects.create(
            title='TestSletteListe',
            owner=self.owner
        )
        item_name = 'Sjokolade'
        item_amount = '1 stk'
        self.item = Item.objects.create(
            name=item_name,
            amount=item_amount
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
            }, follow=True
        )
        bool_item_added = self.item in response.context['item_list']
        self.assertTrue(bool_item_added)
        self.assertEquals(response.status_code, 200)
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
        }, follow=True)
        # Tests that list is shared with participant one
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
        # Tests that list is shared with participant two
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, self.detail_shopping_list_url)
        # Tests that list is shared with participant three
        self.assertEqual(response3.status_code, 200)
        self.assertRedirects(response3, self.detail_shopping_list_url)
        # Check that none of the users are in participants
        bool_users_not_admin = (self.participants_en and self.participants_to) not in self.shopping_list.admins.all()
        self.assertTrue(bool_users_not_admin)
        bool_users_participants = (self.participants_en and self.participants_to) in self.shopping_list.participants.all()
        self.assertTrue(bool_users_participants)
        # Check if shopping list's owner is correct
        bool_owner = self.owner == self.shopping_list.owner
        self.assertTrue(bool_owner)

    def test_make_user_admin_of_shopping_list_POST(self):
        # Share shopping list with self.participant_en
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })
        # Share shopping list with self.admin (admin is only a participator for now)
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        # Owner of shopping list makes self.admin admin
        self.make_user_admin_of_shopping_list_url_1 = reverse('make-admin', args=['1', self.admin])
        response = self.client.post(self.make_user_admin_of_shopping_list_url_1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list_url)
        # Check that self.admin is in the list of admins in shopping list
        bool_admin_i_adminliste = (self.admin in self.shopping_list.admins.all()) and (self.admin not in self.shopping_list.participants.all())
        self.assertTrue(bool_admin_i_adminliste)

    def test_remove_user_from_list_POST(self):
        # Share shopping list with self.participants_en, self.participants_to and self.admin
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_en
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.participants_to
        })
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        # Remove participants_en from shopping list
        self.remove_user_from_list_url = reverse('remove-user-from-shopping-list', args=['1', self.participants_en])
        response_remove = self.client.post(self.remove_user_from_list_url)
        self.assertEqual(response_remove.status_code, 302)
        self.assertRedirects(response_remove, self.detail_shopping_list_url)

        # Check if participants_en still has been removes from the list of participants of shopping list
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
        # Adds user as participant
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        # Makes user admin
        self.make_user_admin_of_shopping_list_url = reverse('make-admin', args=['1', self.admin])
        self.client.post(self.make_user_admin_of_shopping_list_url)
        # Admin leaves list
        self.remove_user_from_list_url = reverse('remove-user-from-shopping-list', args=['1', self.admin])
        response_remove = self.client.post(self.remove_user_from_list_url)
        # Test if admin has left the shopping list
        self.assertEqual(response_remove.status_code, 302)
        self.assertRedirects(response_remove, self.detail_shopping_list_url)
        bool_is_removed = (self.admin not in self.shopping_list.participants.all()) and (
                    self.shopping_list not in ShoppingList.get_user_shopping_lists(self.admin))
        self.assertTrue(bool_is_removed)

    def test_owner_leaves_list_POST(self):
        # Add self.admin to shopping list as participant
        self.client.post(self.share_shopping_list_url, {
            'username': self.admin
        })
        # Promote self.admin to admin of shopping list
        self.make_user_admin_of_shopping_list_url = reverse('make-admin', args=['1', self.admin])
        self.client.post(self.make_user_admin_of_shopping_list_url)
        # As owner of shopping list (self.owner), transfer ownership to self.admin
        self.change_owner_of_shopping_list_url = reverse('change-owner', args=['1', self.admin])
        response_change_owner = self.client.post(self.change_owner_of_shopping_list_url)
        # Check redirection of page and status code
        self.assertEquals(response_change_owner.status_code, 302)
        self.assertRedirects(response_change_owner, self.index_url)
        # Check if ownership has been transferred
        bool_owner_is_removed = (self.shopping_list not in ShoppingList.get_user_shopping_lists(self.owner)) and (self.shopping_list not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list in ShoppingList.get_user_shopping_lists(self.admin)) and (self.shopping_list in ShoppingList.objects.filter(owner=self.admin)) and (self.admin not in self.shopping_list.admins.all())
        self.assertTrue(bool_owner_is_removed)
        self.assertTrue(bool_admin_is_owner)


class CommentViews(TestCase):

    def setUp(self):
        # Making users that can be used in tests
        self.owner = User.objects.create_user(username='testowner', password='12345testing')
        self.participants_en = User.objects.create_user(username='testparticipant1', password='12345testing')
        self.participants_to = User.objects.create_user(username='testparticipant2', password='12345testing')
        self.admin = User.objects.create_user(username='testadmin1', password='12345testing');
        # Create client. Owner logs in.
        self.client = Client()
        self.client.login(username='testowner', password='12345testing')
        # Shopping list urls
        self.detail_shopping_list_url = reverse('detail', args='1')
        self.share_shopping_list_url = reverse('share-shopping-list', args='1')
        # Create shopping list
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        # Create comment
        self.comment_content = 'What a cool shoppinglist, and what a page! But can handle comments?'
        self.comment = Comment.objects.create(
            author=self.owner,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        # Create reply
        self.reply_content = 'Well of course you can'
        self.reply = Reply.objects.create(
            author=self.participants_to,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.add_comment_url = reverse('add-comment', args='1')

    def test_add_comment_POST(self):
        # Add a comment on a shopping list
        self.add_comment_url = reverse('add-comment', args='1')
        response = self.client.post(self.add_comment_url, {
            'content': self.comment_content
        }, follow=True)
        # Check if comment has been added
        bool_comment_added = self.comment in response.context['comments']
        self.assertTrue(bool_comment_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_delete_comment_POST(self):
        # Make a comment
        self.add_comment_url = reverse('add-comment', args='1')
        self.client.post(self.add_comment_url, {
            'content': self.comment_content
        })
        # Delete the comment
        delete_comment_url = reverse('delete-comment', args=['1', '1'])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

    def test_reply_comment_POST(self):
        # Make a comment
        self.client.post(self.add_comment_url, {
            'content': self.comment_content
        })
        # Reply to the comment
        self.reply_url = reverse('reply', args=['1', '1'])
        response = self.client.post(self.reply_url, {
            'content': self.reply_content
        }, follow=True)
        # Check if comment has been replied to
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_replied = self.reply in replies
        self.assertTrue(bool_comment_is_replied)

    def test_delete_reply_POST(self):
        # Make a comment
        self.client.post(self.add_comment_url, {
            'content': self.comment_content
        })
        # Reply to the comment
        self.reply_url = reverse('reply', args=['1', '1'])
        self.client.post(self.reply_url, {
            'content': self.reply_content
        })
        delete_reply_url = reverse('delete-reply', args=['1', '1'])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply not in replies
        self.assertTrue(bool_comment_is_removed)
