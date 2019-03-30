from django.test import TestCase, Client
from django.urls import reverse
from shopping_list.models import Item, ShoppingList
from shopping_list.views import *
from django.contrib.auth import get_user_model
User = get_user_model()


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
