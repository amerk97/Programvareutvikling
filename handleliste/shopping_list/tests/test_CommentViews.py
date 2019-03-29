from django.test import TestCase, Client
from django.urls import reverse
from shopping_list.models import ShoppingList, Comment
from shopping_list.views import *
from django.contrib.auth import get_user_model
User = get_user_model()


class CommentViews(TestCase):

    def setUp(self):
        # Making users that can be used in tests
        self.password = '12345testing'
        self.owner = User.objects.create_user(username='testowner', password=self.password)
        self.participant1 = User.objects.create_user(username='testparticipant1', password=self.password)
        self.participant2 = User.objects.create_user(username='testparticipant2', password=self.password)
        self.admin1 = User.objects.create_user(username='testadmin1', password=self.password)
        self.admin2 = User.objects.create_user(username='testadmin2', password=self.password)
        self.outsider = User.objects.create_user(username='testoutsider', password=self.password)
        # Create client. Login as owner
        self.client = Client()
        self.client.login(username='testowner', password=self.password)
        # Create shopping list
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        # Urls
        self.detail_shopping_list_url = reverse('detail', args=str(self.shopping_list.id))
        self.index_url = reverse('index')
        self.add_comment_url = reverse('add-comment', args=str(self.shopping_list.id))
        # Add participants and admins
        self.shopping_list.participants.add(self.participant1)
        self.shopping_list.participants.add(self.participant2)
        self.shopping_list.admins.add(self.admin1)
        self.shopping_list.admins.add(self.admin2)
        # Create comments
        self.comment_content = 'What a cool shoppinglist, and what a page! But can handle comments?'
        self.comment = Comment.objects.create(
            author=self.owner,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        self.comment_participant1 = Comment.objects.create(
            author=self.participant1,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        self.comment_admin1 = Comment.objects.create(
            author=self.admin1,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        self.comment_admin2 = Comment.objects.create(
            author=self.admin2,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        self.comment_outsider = Comment.objects.create(
            author=self.outsider,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        self.comment_outsider.delete()

    def test_add_comment_POST(self):
        # Delete previous comments from database
        self.comment.delete()
        self.comment_participant1.delete()
        self.comment_admin1.delete()
        # Change their id to match auto_generated id when new comment are made
        self.comment.id = 6
        self.comment_participant1.id = 7
        self.comment_admin1.id = 8
        self.comment_outsider.id = 9

        # Attempt to add a comment on a shopping list as owner
        self.add_comment_url = reverse('add-comment', args=str(self.shopping_list.id))
        response = self.client.post(self.add_comment_url, {
            'content': self.comment_content
        }, follow=True)
        # Check if comment has been added
        bool_comment_added = self.comment in response.context['comments']
        self.assertTrue(bool_comment_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Login as participant1
        self.client.login(username=self.participant1.username, password=self.password)
        # Attempt to add a comment on a shopping list as participant
        self.add_comment_url = reverse('add-comment', args=str(self.shopping_list.id))
        response = self.client.post(self.add_comment_url, {
            'content': self.comment_content
        }, follow=True)
        # Check if comment has been added
        bool_comment_added = self.comment_participant1 in response.context['comments']
        self.assertTrue(bool_comment_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Login as admin1
        self.client.login(username=self.admin1.username, password=self.password)
        # Attempt to add a comment on a shopping list as admin
        self.add_comment_url = reverse('add-comment', args=str(self.shopping_list.id))
        response = self.client.post(self.add_comment_url, {
            'content': self.comment_content
        }, follow=True)
        # Check if comment has been added
        bool_comment_added = self.comment_admin1 in response.context['comments']
        self.assertTrue(bool_comment_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Login as outsider
        self.client.login(username=self.outsider.username, password=self.password)
        # Attempt to add a comment on a shopping list as not a member of shopping list
        self.add_comment_url = reverse('add-comment', args=str(self.shopping_list.id))
        response = self.client.post(self.add_comment_url, {
            'content': self.comment_content
        }, follow=True)
        # Check if comment has not been added
        bool_comment_added = self.comment_outsider not in Comment.objects.filter(pk=self.comment_outsider.id)
        self.assertTrue(bool_comment_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

    def test_delete_comment_as_participant(self):
        # Login as participant2
        self.client.login(username=self.participant2.username, password=self.password)
        # Attempt to delete participant1's comment as another participant (participant2)
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_participant1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_participant1 not in response.context['comments']
        self.assertFalse(bool_comment_is_removed)

        # Login as participant1
        self.client.login(username=self.participant1.username, password=self.password)
        # Attempt to delete own comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_participant1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_participant1 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete admin's comment as participant
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_admin1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_admin1 not in response.context['comments']
        self.assertFalse(bool_comment_is_removed)

        # Delete owner's comment as participant
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment not in response.context['comments']
        self.assertFalse(bool_comment_is_removed)

    def test_delete_comment_as_owner(self):
        # Already logged in as owner
        # Attempt to delete participant1's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_participant1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_participant1 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete admin's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_admin1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_admin1 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete own comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

    def test_delete_comment_as_admin(self):
        # Login as admin1
        self.client.login(username=self.admin1.username, password=self.password)
        # Attempt to delete participant's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_participant1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_participant1 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete own comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_admin1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_admin1 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete another admin's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_admin2.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment_admin2 not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

        # Attempt to delete owner's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        bool_comment_is_removed = self.comment not in response.context['comments']
        self.assertTrue(bool_comment_is_removed)

    def test_delete_comment_as_outsider(self):
        # Login as outsider
        self.client.login(username=self.outsider.username, password=self.password)

        # Attempt to delete participant's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_participant1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.comment_participant1 not in Comment.objects.filter(pk=self.comment_participant1.id)
        self.assertFalse(bool_comment_is_removed)

        # Attempt to delete admin's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment_admin1.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.comment_admin1 not in Comment.objects.filter(pk=self.comment_admin1.id)
        self.assertFalse(bool_comment_is_removed)

        # Attempt to delete owner's comment
        delete_comment_url = reverse('delete-comment', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(delete_comment_url, follow=True)
        # Check if comment has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.comment not in Comment.objects.filter(pk=self.comment.id)
        self.assertFalse(bool_comment_is_removed)
