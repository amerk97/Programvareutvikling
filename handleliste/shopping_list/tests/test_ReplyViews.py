from django.test import TestCase, Client
from django.urls import reverse
from shopping_list.models import ShoppingList, Comment, Reply
from shopping_list.views import *
from django.contrib.auth import get_user_model
User = get_user_model()


class ReplyViews(TestCase):

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
        self.index_url = reverse('index')
        self.detail_shopping_list_url = reverse('detail', args=str(self.shopping_list.id))
        # Add participants and admins
        self.shopping_list.participants.add(self.participant1)
        self.shopping_list.participants.add(self.participant2)
        self.shopping_list.admins.add(self.admin1)
        self.shopping_list.admins.add(self.admin2)
        # Create comments
        self.comment_content = 'What a cool shopping list, and what a page! But can handle comments?'
        self.comment = Comment.objects.create(
            author=self.owner,
            content=self.comment_content,
            shopping_list=self.shopping_list
        )
        # Create reply
        self.reply_content = 'Well of course you can'
        self.reply = Reply.objects.create(
            author=self.owner,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_participant1 = Reply.objects.create(
            author=self.participant1,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_participant2 = Reply.objects.create(
            author=self.participant2,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_admin1 = Reply.objects.create(
            author=self.admin1,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_admin2 = Reply.objects.create(
            author=self.admin2,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_outsider = Reply.objects.create(
            author=self.outsider,
            content=self.reply_content,
            parent_comment=self.comment
        )
        self.reply_outsider.delete()

    def test_reply(self):
        # Delete replies from database
        self.reply.delete()
        self.reply_participant1.delete()
        self.reply_admin1.delete()
        # Change their id to match the auto_generated id when new replies are made
        self.reply.id = 7
        self.reply_participant1.id = 8
        self.reply_admin1.id = 9
        self.reply_outsider.id = 10

        # Reply to the comment as owner
        self.reply_url = reverse('reply', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(self.reply_url, {
            'content': self.reply_content
        }, follow=True)
        # Check if comment has been replied to
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_replied = self.reply in replies
        self.assertTrue(bool_comment_is_replied)

        # Login as participant
        self.client.login(username=self.participant1.username, password=self.password)
        # Reply to the comment as participant
        self.reply_url = reverse('reply', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(self.reply_url, {
            'content': self.reply_content
        }, follow=True)
        # Check if comment has been replied to
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_replied = self.reply_participant1 in replies
        self.assertTrue(bool_comment_is_replied)

        # Login as admin
        self.client.login(username=self.admin1.username, password=self.password)
        # Reply to the comment as admin
        self.reply_url = reverse('reply', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(self.reply_url, {
            'content': self.reply_content
        }, follow=True)
        # Check if comment has been replied to
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_replied = self.reply_admin1 in replies
        self.assertTrue(bool_comment_is_replied)

        # Login as outsider
        self.client.login(username=self.outsider.username, password=self.password)
        # Reply to the comment as outsider
        self.reply_url = reverse('reply', args=[str(self.shopping_list.id), str(self.comment.id)])
        response = self.client.post(self.reply_url, {
            'content': self.reply_content
        }, follow=True)
        # Check if comment has not been replied to
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_replied = self.reply_outsider in Reply.objects.filter(pk=self.reply_outsider.id)
        self.assertFalse(bool_comment_is_replied)

    def test_delete_reply_as_owner(self):
        # Delete participant reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_participant1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_participant1 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete admin reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_admin1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_admin1 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete own reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply not in replies
        self.assertTrue(bool_comment_is_removed)

    def test_delete_reply_as_admin(self):
        # Login as admin1
        self.client.login(username=self.admin1.username, password=self.password)

        # Delete participant reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_participant1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_participant1 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete own reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_admin1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_admin1 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete another admin's reply (admin2)
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_admin2.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_admin2 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete owner's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply not in replies
        self.assertTrue(bool_comment_is_removed)

    def test_delete_reply_as_participant(self):
        # Login as participant1
        self.client.login(username=self.participant1.username, password=self.password)

        # Delete own reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_participant1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_participant1 not in replies
        self.assertTrue(bool_comment_is_removed)

        # Delete another participant's reply (participant2)
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_participant2.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_participant2 not in replies
        self.assertFalse(bool_comment_is_removed)

        # Delete admin's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_admin1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply_admin1 not in replies
        self.assertFalse(bool_comment_is_removed)

        # Delete owner's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)
        replies = list(response.context['comments'].all())[0].replies()
        bool_comment_is_removed = self.reply not in replies
        self.assertFalse(bool_comment_is_removed)

    def test_delete_reply_as_outsider(self):
        # Login as outsider
        self.client.login(username=self.outsider.username, password=self.password)

        # Delete participant's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_participant1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.reply_participant1 not in Reply.objects.filter(pk=self.reply_participant1.id)
        self.assertFalse(bool_comment_is_removed)

        # Delete admin's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply_admin1.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.reply_admin1 not in Reply.objects.filter(pk=self.reply_admin1.id)
        self.assertFalse(bool_comment_is_removed)

        # Delete owner's reply
        delete_reply_url = reverse('delete-reply', args=[str(self.shopping_list.id), str(self.reply.id)])
        response = self.client.post(delete_reply_url, follow=True)
        # Check if reply has not been deleted
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        bool_comment_is_removed = self.reply not in Reply.objects.filter(pk=self.reply.id)
        self.assertFalse(bool_comment_is_removed)
