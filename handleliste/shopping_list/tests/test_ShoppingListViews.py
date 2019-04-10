from django.test import TestCase, Client
from django.urls import reverse
from shopping_list.models import ShoppingList
from shopping_list.views import *
from django.contrib.auth import get_user_model

User = get_user_model()


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
        self.assertTemplateUsed('shopping_list/shopping_list.html')
        detail_shopping_list1_url = reverse('detail', args=str(self.shopping_list1.id))
        self.assertRedirects(response, detail_shopping_list1_url)
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

    # Check if user has access to shopping list they are a member of
    def test_detail_shopping_list(self):
        # Check if owner of shopping list has access
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shopping_list.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

        # Check if participant of shopping list has access
        self.client.login(username=self.participant1.username, password=self.password)
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shopping_list.html')
        self.assertEquals(response.context['shopping_list'], self.shopping_list1)

        # Check if admin of shopping list has access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(self.detail_shopping_list1_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('shopping_list/shopping_list.html')
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

    def test_change_owner_as_outsider(self):
        self.client.login(username=self.outsider.username, password=self.password)
        # Change owner
        change_owner_url = reverse('change-owner', args=[str(self.shopping_list1.id), self.admin])
        response = self.client.post(change_owner_url, follow=True)
        # Check status code
        self.assertEquals(response.status_code, 200)
        # Check if ownership has not been transferred
        bool_owner_is_removed = (self.shopping_list1 not in ShoppingList.get_user_shopping_lists(self.owner)) \
                                and (self.shopping_list1 not in ShoppingList.objects.filter(owner=self.owner))
        bool_admin_is_owner = (self.shopping_list1 in ShoppingList.get_user_shopping_lists(self.admin)) \
                              and (self.shopping_list1 in ShoppingList.objects.filter(owner=self.admin)) \
                              and (self.admin not in self.shopping_list1.admins.all())
        self.assertFalse(bool_owner_is_removed)
        self.assertFalse(bool_admin_is_owner)
