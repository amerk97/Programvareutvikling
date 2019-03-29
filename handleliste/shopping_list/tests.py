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
        self.password = '12345testing'
        self.owner = User.objects.create_user(username='testowner', password=self.password)
        self.participant1 = User.objects.create_user(username='testparticipant1', password=self.password)
        self.participant2 = User.objects.create_user(username='testparticipant2', password=self.password)
        self.admin = User.objects.create_user(username='testadmin1', password=self.password)
        self.outsider = User.objects.create_user(username='testoutsider', password=self.password)
        # Create client and log in with owner
        self.client = Client()
        self.client.login(username='testowner', password=self.password)
        # Create shopping lists
        self.shopping_list1 = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        self.shopping_list2 = ShoppingList.objects.create(
            title='TestSletteListe',
            owner=self.owner
        )
        # Add participants and admin
        self.shopping_list1.participants.add(self.participant1)
        self.shopping_list1.participants.add(self.participant2)
        self.shopping_list1.admins.add(self.admin)
        # Shopping list urls
        self.detail_shopping_list1_url = reverse('detail', args=str(self.shopping_list1.id))
        self.detail_shopping_list2_url = reverse('detail', args=str(self.shopping_list2.id))
        self.share_shopping_list1_url = reverse('share-shopping-list', args=str(self.shopping_list1.id))
        self.share_shopping_list2_url = reverse('share-shopping-list', args=str(self.shopping_list2.id))
        self.index_url = reverse('index')
        self.delete_shopping_list1_url = reverse('delete-shopping-list', args=str(self.shopping_list1.id))

    def test_create_shopping_list(self):
        # Delete shopping list from database
        self.shopping_list1.delete()
        # Change id to match the auto-generated id when new list is made
        self.shopping_list1.id = 3
        # Create new shopping list
        self.create_list_url = reverse('create-list')
        response = self.client.post(self.create_list_url, {
            'title': self.shopping_list1.title
        }, follow=True)
        # Check if the new shopping list has been created
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shoppinglist.html')
        detail_shopping_list1_url = reverse('detail', args=str(self.shopping_list1.id))
        self.assertRedirects(response, detail_shopping_list1_url)
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

    # Check if user has access to shopping list they are a member of
    def test_detail_shopping_list(self):
        # Check if owner of shopping list has access
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shoppinglist.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

        # Check if participant of shopping list has access
        self.client.login(username=self.participant1.username, password=self.password)
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shoppinglist.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

        # Check if admin of shopping list has access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shoppinglist.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

        # Check if outsider does not have access
        self.client.login(username=self.outsider.username, password=self.password)
        response = self.client.post(self.detail_shopping_list1_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/index.html')
        self.assertRedirects(response, self.index_url)

    def test_share_shopping_list_as_owner(self):
        # Share shopping list with outsider
        response = self.client.post(self.share_shopping_list2_url, {
            'username': self.outsider
        }, follow=True)
        # Tests that list is shared with outsider
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list2_url)
        # Check that outsider is a participant of the list
        bool_is_participant = self.outsider in self.shopping_list2.participants.all()
        self.assertTrue(bool_is_participant)
        # Check that outsider is not an admin of the list
        bool_is_not_admin = self.outsider not in self.shopping_list2.admins.all()
        self.assertTrue(bool_is_not_admin)
        # Check if shopping list's owner is correct
        bool_owner = self.owner == self.shopping_list2.owner
        self.assertTrue(bool_owner)

    def test_share_shopping_list_as_admin(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(self.share_shopping_list1_url, {
            'username': self.outsider
        }, follow=True)
        # Tests that list is shared with outsider
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that outsider is a participant of the list
        bool_is_participant = self.outsider in self.shopping_list1.participants.all()
        self.assertTrue(bool_is_participant)
        # Check that outsider is not an admin of the list
        bool_is_not_admin = self.outsider not in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_not_admin)
        # Check if shopping list's owner is correct
        bool_owner = self.owner == self.shopping_list1.owner
        self.assertTrue(bool_owner)

    def test_share_shopping_list_as_participant(self):
        self.client.login(username=self.participant1.username, password=self.password)
        response = self.client.post(self.share_shopping_list1_url, {
            'username': self.outsider
        }, follow=True)
        # Tests that list is shared with outsider
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that outsider is a participant of the list
        bool_is_participant = self.outsider in self.shopping_list1.participants.all()
        self.assertTrue(bool_is_participant)
        # Check that outsider is not an admin of the list
        bool_is_not_admin = self.outsider not in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_not_admin)
        # Check if shopping list's owner is correct
        bool_owner = self.owner == self.shopping_list1.owner
        self.assertTrue(bool_owner)

    def test_share_shopping_list_as_outsider(self):
        self.client.login(username=self.outsider.username, password=self.password)
        response = self.client.post(self.share_shopping_list2_url, {
            'username': self.outsider
        }, follow=True)
        # Tests that list is not shared with outsider
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check that outsider is not a participant of the list
        bool_is_participant = self.outsider in self.shopping_list2.participants.all()
        self.assertFalse(bool_is_participant)
        # Check that outsider is not an admin of the list
        bool_is_not_admin = self.outsider not in self.shopping_list2.admins.all()
        self.assertTrue(bool_is_not_admin)
        # Check if shopping list's owner is correct
        bool_owner = self.owner == self.shopping_list2.owner
        self.assertTrue(bool_owner)

    def test_make_user_admin_as_owner(self):
        # Promote participant1 to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that participant1 is an admin of the shopping list and not a participant anymore
        bool_is_admin = (self.participant1 in self.shopping_list1.admins.all()) and (self.admin not in self.shopping_list1.participants.all())
        self.assertTrue(bool_is_admin)

        # Promote admin to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that admin is still an admin of the shopping list
        bool_is_admin = self.admin in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_admin)

        # Promote outsider to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.outsider])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that outsider is not an admin of the shopping list
        bool_is_admin = self.outsider in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

        # Promote owner to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that owner is not an admin of the shopping list
        bool_is_admin = self.owner in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

    def test_make_user_admin_as_admin(self):
        self.client.login(username=self.admin.username, password=self.password)
        # Promote participant1 to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that participant1 is an admin of the shopping list and not a participant anymore
        bool_is_admin = (self.participant1 in self.shopping_list1.admins.all()) and (self.admin not in self.shopping_list1.participants.all())
        self.assertTrue(bool_is_admin)

        # Promote admin to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that admin is still an admin of the shopping list
        bool_is_admin = self.admin in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_admin)

        # Promote outsider to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.outsider])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that outsider is not an admin of the shopping list
        bool_is_admin = self.outsider in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

        # Promote owner to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that owner is not an admin of the shopping list
        bool_is_admin = self.owner in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

    def test_make_user_admin_as_participant(self):
        self.client.login(username=self.participant1, password=self.password)
        # Promote participant1 to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.participant2])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that participant1 is an admin of the shopping list and not a participant anymore
        bool_is_admin = (self.participant2 in self.shopping_list1.admins.all()) and (self.admin not in self.shopping_list1.participants.all())
        self.assertFalse(bool_is_admin)

        # Promote admin to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that admin is still an admin of the shopping list
        bool_is_admin = self.admin in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_admin)

        # Promote outsider to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.outsider])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that outsider is not an admin of the shopping list
        bool_is_admin = self.outsider in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

        # Promote owner to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check that owner is not an admin of the shopping list
        bool_is_admin = self.owner in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

    def test_make_user_admin_as_outsider(self):
        self.client.login(username=self.outsider, password=self.password)
        # Promote participant1 to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.participant2])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check that participant1 is an admin of the shopping list and not a participant anymore
        bool_is_admin = (self.participant2 in self.shopping_list1.admins.all()) and (self.admin not in self.shopping_list1.participants.all())
        self.assertFalse(bool_is_admin)

        # Promote admin to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check that admin is still an admin of the shopping list
        bool_is_admin = self.admin in self.shopping_list1.admins.all()
        self.assertTrue(bool_is_admin)

        # Promote outsider to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.outsider])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check that outsider is not an admin of the shopping list
        bool_is_admin = self.outsider in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

        # Promote owner to admin
        make_admin_url = reverse('make-admin', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(make_admin_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check that owner is not an admin of the shopping list
        bool_is_admin = self.owner in self.shopping_list1.admins.all()
        self.assertFalse(bool_is_admin)

    def test_remove_user_from_list_as_owner(self):
        # Remove participant1 from shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if participant1 has been removed from the shopping list
        bool_is_removed = (self.participant1 not in self.shopping_list1.participants.all()) and (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.participant1))
        self.assertTrue(bool_is_removed)

        # Remove admin from shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if admin has been removed from the shopping list
        bool_is_removed = (self.admin not in self.shopping_list1.admins.all()) and (
                    self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.admin))
        self.assertTrue(bool_is_removed)

        # Leave shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check if owner has not been removed from the shopping list
        bool_is_removed = self.owner != self.shopping_list1.owner and self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)
        self.assertFalse(bool_is_removed)

    def test_remove_user_from_list_as_admin(self):
        self.client.login(username=self.admin.username, password=self.password)
        # Remove participant1 from shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if participant1 has been removed from the shopping list
        bool_is_removed = (self.participant1 not in self.shopping_list1.participants.all()) and (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.participant1))
        self.assertTrue(bool_is_removed)

        # Remove owner of shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if owner has not been removed from the shopping list
        bool_is_removed = self.owner != self.shopping_list1.owner and self.shopping_list1 not in ShoppingList.get_user_shopping_lists(
            self.owner)
        self.assertFalse(bool_is_removed)

        # Leave shopping list (and remove admin)
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check if admin has been removed from the shopping list
        bool_is_removed = (self.admin not in self.shopping_list1.admins.all()) and (
                    self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.admin))
        self.assertTrue(bool_is_removed)

    def test_remove_user_from_list_as_participant(self):
        self.client.login(username=self.participant1.username, password=self.password)
        # Remove owner of shopping list
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.owner])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if owner has not been removed from the shopping list
        bool_is_removed = self.owner != self.shopping_list1.owner and self.shopping_list1 not in ShoppingList.get_user_shopping_lists(
            self.owner)
        self.assertFalse(bool_is_removed)

        # Remove admin
        remove_user_url = reverse('remove-user-from-shopping-list', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if admin has been removed from the shopping list
        bool_is_removed = (self.admin not in self.shopping_list1.admins.all()) and (
                    self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.admin))
        self.assertFalse(bool_is_removed)

        # Leave shopping list
        remove_user_url = reverse('remove-user-from-shopping-list',
                                  args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(remove_user_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        # Check if participant1 has been removed from the shopping list
        bool_is_removed = (self.participant1 not in self.shopping_list1.participants.all()) and (
                    self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.participant1))
        self.assertTrue(bool_is_removed)

    def test_delete_shopping_list(self):
        # Delete shopping list as outsider
        self.client.login(username=self.outsider.username, password=self.password)
        response = self.client.post(self.delete_shopping_list1_url, follow=True)
        # Check if list has not been deleted
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        shopping_list_is_deleted = self.shopping_list1 not in ShoppingList.objects.filter(pk=self.shopping_list1.id)
        self.assertFalse(shopping_list_is_deleted)

        # Delete shopping list as participant
        self.client.login(username=self.participant1.username, password=self.password)
        response = self.client.post(self.delete_shopping_list1_url, follow=True)
        # Check if list has not been deleted
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        shopping_list_is_deleted = self.shopping_list1 not in ShoppingList.objects.filter(pk=self.shopping_list1.id)
        self.assertFalse(shopping_list_is_deleted)

        # Delete shopping list as admin
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(self.delete_shopping_list1_url, follow=True)
        # Check if list has not been deleted
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        shopping_list_is_deleted = self.shopping_list1 not in ShoppingList.objects.filter(pk=self.shopping_list1.id)
        self.assertFalse(shopping_list_is_deleted)

        # Delete shopping list as owner
        self.client.login(username=self.owner.username, password=self.password)
        response = self.client.post(self.delete_shopping_list1_url, follow=True)
        # Check if list has been deleted
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.index_url)
        shopping_list_is_deleted = self.shopping_list1 not in ShoppingList.objects.filter(pk=self.shopping_list1.id)
        self.assertTrue(shopping_list_is_deleted)

    def test_change_owner_as_owner(self):
        # As owner of shopping list, transfer ownership to participant
        change_owner_url = reverse('change-owner', args=[str(self.shopping_list1.id), self.participant1])
        response = self.client.post(change_owner_url)
        # Check redirection of page and status code
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.detail_shopping_list1_url)
        # Check if ownership has been transferred
        bool_owner_is_removed = (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)) \
                                and (self.shopping_list1 not in ShoppingList.objects.filter(owner=self.owner))
        bool_participant1_is_owner = (self.shopping_list1 in ShoppingList.get_user_shopping_lists(self.participant1)) \
                              and (self.shopping_list1 in ShoppingList.objects.filter(owner=self.participant1)) \
                              and (self.participant1 not in self.shopping_list1.participants.all())
        self.assertFalse(bool_owner_is_removed)
        self.assertFalse(bool_participant1_is_owner)

        # As owner of shopping list (self.owner), transfer ownership to self.admin
        change_owner_url = reverse('change-owner', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(change_owner_url)
        # Check redirection of page and status code
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.index_url)
        # Check if ownership has been transferred
        bool_owner_is_removed = (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)) \
                                and (self.shopping_list1 not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list1 in ShoppingList.get_user_shopping_lists(self.admin)) \
                              and (self.shopping_list1 in ShoppingList.objects.filter(owner=self.admin)) \
                              and (self.admin not in self.shopping_list1.admins.all())
        self.assertTrue(bool_owner_is_removed)
        self.assertTrue(bool_admin_is_owner)

    def test_change_owner_as_admin(self):
        self.client.login(username=self.admin.username, password=self.password)
        # Change owner
        change_owner_url = reverse('change-owner', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(change_owner_url, follow=True)
        # Check status code
        self.assertEquals(response.status_code, 403)
        # Check if ownership has not been transferred
        bool_owner_is_removed = (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)) \
                                and (self.shopping_list1 not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list1 in ShoppingList.get_user_shopping_lists(self.admin)) \
                              and (self.shopping_list1 in ShoppingList.objects.filter(owner=self.admin)) \
                              and (self.admin not in self.shopping_list1.admins.all())
        self.assertFalse(bool_owner_is_removed)
        self.assertFalse(bool_admin_is_owner)

    def test_change_owner_as_participant(self):
        self.client.login(username=self.participant1.username, password=self.password)
        # Change owner
        change_owner_url = reverse('change-owner', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(change_owner_url, follow=True)
        # Check status code
        self.assertEquals(response.status_code, 403)
        # Check if ownership has not been transferred
        bool_owner_is_removed = (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)) \
                                and (self.shopping_list1 not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list1 in ShoppingList.get_user_shopping_lists(self.admin)) \
                              and (self.shopping_list1 in ShoppingList.objects.filter(owner=self.admin)) \
                              and (self.admin not in self.shopping_list1.admins.all())
        self.assertFalse(bool_owner_is_removed)
        self.assertFalse(bool_admin_is_owner)


class ItemViews(TestCase):

    def setUp(self):
        # Create users
        self.password = '12345testing'
        self.owner = User.objects.create_user(username='testowner', password=self.password)
        self.participant1 = User.objects.create_user(username='testparticipant1', password=self.password)
        self.participant2 = User.objects.create_user(username='testparticipant2', password=self.password)
        self.admin1 = User.objects.create_user(username='testadmin1', password=self.password)
        self.admin2 = User.objects.create_user(username='testadmin2', password=self.password)
        self.outsider = User.objects.create_user(username='testoutsider', password=self.password)
        # Create client and log in with owner
        self.client = Client()
        self.client.login(username='testowner', password=self.password)
        # Create shopping lists
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        # Add participants and admin
        self.shopping_list.participants.add(self.participant1)
        self.shopping_list.participants.add(self.participant2)
        self.shopping_list.admins.add(self.admin1)
        self.shopping_list.admins.add(self.admin2)
        # Create items
        self.item_name = 'Sjokolade'
        self.item_amount = '1 stk'
        self.item = Item.objects.create(
            creator=self.owner,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_participant1 = Item.objects.create(
            creator=self.participant1,
            name=self.item_name,
            amount=self.item_amount
        )
        self.item_participant2 = Item.objects.create(
            creator=self.participant2,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_admin1 = Item.objects.create(
            creator=self.admin1,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_admin2 = Item.objects.create(
            creator=self.admin2,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_outsider = Item.objects.create(
            creator=self.outsider,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_outsider.delete()
        # Urls
        self.detail_shopping_list_url = reverse('detail', args=str(self.shopping_list.id))
        self.index_url = reverse('index')

    def test_add_item(self):
        # Delete items from database
        self.item.delete()
        self.item_participant1.delete()
        self.item_admin1.delete()
        # Change items' id to match auto-generated id when creating new item
        self.item.id = 7
        self.item_participant1.id = 8
        self.item_admin1.id = 9
        self.item_outsider.id = 10

        # Add item as owner
        add_url = reverse('add', args=str(self.shopping_list.id))
        response = self.client.post(add_url, {
            'name': self.item_name,
            'amount': self.item_amount
            }, follow=True
        )
        # Check if item has been added
        bool_item_added = self.item in response.context['item_list'] \
                          and self.item in Item.objects.filter(pk=self.item.id)
        self.assertTrue(bool_item_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Add item as participant
        self.client.login(username=self.participant1.username, password=self.password)
        add_url = reverse('add', args=str(self.shopping_list.id))
        response = self.client.post(add_url, {
            'name': self.item_name,
            'amount': self.item_amount
            }, follow=True
        )
        # Check if item has been added
        bool_item_added = self.item_participant1 in response.context['item_list'] \
                          and self.item_participant1 in Item.objects.filter(pk=self.item_participant1.id)
        self.assertTrue(bool_item_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Add item as admin
        self.client.login(username=self.admin1.username, password=self.password)
        add_url = reverse('add', args=str(self.shopping_list.id))
        response = self.client.post(add_url, {
            'name': self.item_name,
            'amount': self.item_amount
            }, follow=True
        )
        # Check if item has been added
        bool_item_added = self.item_admin1 in response.context['item_list'] \
                          and self.item_admin1 in Item.objects.filter(pk=self.item_admin1.id)
        self.assertTrue(bool_item_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Add item as outsider
        self.client.login(username=self.outsider.username, password=self.password)
        add_url = reverse('add', args=str(self.shopping_list.id))
        response = self.client.post(add_url, {
            'name': self.item_name,
            'amount': self.item_amount
            }, follow=True
        )
        # Check if item has not been added
        bool_item_added = self.item_outsider in Item.objects.filter(pk=self.item_outsider.id)
        self.assertFalse(bool_item_added)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

    def test_delete_item_as_owner(self):
        # Delete participant's item
        delete_url = reverse('delete-item', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_participant1 not in response.context['item_list'] \
                            and self.item_participant1 not in Item.objects.filter(pk=self.item_participant1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete admin's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete own item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete item that doesn't exist
        delete_url = reverse('delete-item', args=['20', str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if user is redirected correctly
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_delete_item_as_admin(self):
        self.client.login(username=self.admin1.username, password=self.password)
        # Delete participant's item
        delete_url = reverse('delete-item', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_participant1 not in response.context['item_list'] \
                            and self.item_participant1 not in Item.objects.filter(pk=self.item_participant1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete admin's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete own item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete item that doesn't exist
        delete_url = reverse('delete-item', args=['20', str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if user is redirected correctly
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_delete_item_as_participant(self):
        self.client.login(username=self.participant1.username, password=self.password)
        # Delete own item
        delete_url = reverse('delete-item', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_participant1 not in response.context['item_list'] \
                            and self.item_participant1 not in Item.objects.filter(pk=self.item_participant1.id)
        self.assertTrue(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete another participant's item
        delete_url = reverse('delete-item', args=[str(self.item_participant2.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_participant2 not in response.context['item_list'] \
                            and self.item_participant2 not in Item.objects.filter(pk=self.item_participant2.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete admin's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete owner's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in response.context['item_list'] \
                            and self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Delete item that doesn't exist
        delete_url = reverse('delete-item', args=['20', str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if user is redirected correctly
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_delete_item_as_outsider(self):
        self.client.login(username=self.outsider.username, password=self.password)
        # Delete participant's item
        delete_url = reverse('delete-item', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_participant1 not in Item.objects.filter(pk=self.item_participant1.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Delete admin's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Delete owner's item
        delete_url = reverse('delete-item', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_admin1 not in Item.objects.filter(pk=self.item_admin1.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Delete item that doesn't exist
        delete_url = reverse('delete-item', args=['20', str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if user is redirected correctly
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Delete item that outsider has created, but no longer is a part of the shopping list
        self.item_outsider.save()
        delete_url = reverse('delete-item', args=[str(self.item_outsider.id), str(self.shopping_list.id)])
        response = self.client.post(delete_url, follow=True)
        # Check if item has been deleted
        bool_item_deleted = self.item_outsider not in Item.objects.filter(pk=self.item_outsider.id)
        self.assertFalse(bool_item_deleted)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

    def test_bought_item_as_owner(self):
        # Mark participant's item as bought
        bought_url = reverse('bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as bought
        bought_url = reverse('bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as bought
        bought_url = reverse('bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_bought_item_as_admin(self):
        self.client.login(username=self.admin1.username, password=self.password)
        # Mark participant's item as bought
        bought_url = reverse('bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as bought
        bought_url = reverse('bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as bought
        bought_url = reverse('bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_bought_item_as_participant(self):
        self.client.login(username=self.participant1.username, password=self.password)
        # Mark participant's item as bought
        bought_url = reverse('bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as bought
        bought_url = reverse('bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as bought
        bought_url = reverse('bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_bought_item_as_outsider(self):
        self.client.login(username=self.outsider.username, password=self.password)
        # Mark participant's item as bought
        bought_url = reverse('bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item_participant1.id)[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Mark admin's item as bought
        bought_url = reverse('bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item_admin1.id)[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Mark owner's item as bought
        bought_url = reverse('bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item.id)[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

    def test_not_bought_item_as_owner(self):
        # Set all items as bought and save changes to the database
        self.item.bought = True
        self.item_participant1.bought = True
        self.item_admin1.bought = True
        self.item.save()
        self.item_participant1.save()
        self.item_admin1.save()

        # Mark participant's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_not_bought_item_as_admin(self):
        # Set all items as bought and save changes to the database
        self.item.bought = True
        self.item_participant1.bought = True
        self.item_admin1.bought = True
        self.item.save()
        self.item_participant1.save()
        self.item_admin1.save()

        self.client.login(username=self.admin1.username, password=self.password)
        # Mark participant's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_not_bought_item_as_participant(self):
        # Set all items as bought and save changes to the database
        self.item.bought = True
        self.item_participant1.bought = True
        self.item_admin1.bought = True
        self.item.save()
        self.item_participant1.save()
        self.item_admin1.save()

        self.client.login(username=self.participant1.username, password=self.password)
        # Mark participant's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[1].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark admin's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[3].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

        # Mark owner's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = list(response.context['item_list'])[0].bought
        self.assertFalse(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.detail_shopping_list_url)

    def test_not_bought_item_as_outsider(self):
        # Set all items as bought and save changes to the database
        self.item.bought = True
        self.item_participant1.bought = True
        self.item_admin1.bought = True
        self.item.save()
        self.item_participant1.save()
        self.item_admin1.save()

        self.client.login(username=self.outsider.username, password=self.password)
        # Mark participant's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_participant1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item_participant1.id)[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Mark admin's item as not bought
        not_bought_url = reverse('not-bought', args=[str(self.item_admin1.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item_admin1.id)[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)

        # Mark owner's item as not bought
        not_bought_url = reverse('bought', args=[str(self.item.id), str(self.shopping_list.id)])
        response = self.client.post(not_bought_url, follow=True)
        # Check if item is bought
        bool_is_bought = Item.objects.filter(pk=self.item.id)[0].bought
        self.assertTrue(bool_is_bought)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, self.index_url)


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
