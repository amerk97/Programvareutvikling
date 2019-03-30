from django.test import TestCase, Client
from shopping_list.models import ShoppingList, Item
from shopping_list.views import *
from django.contrib.auth import get_user_model
User = get_user_model()


class ShoppingListModels(TestCase):

    def setUp(self):
        # Create users
        self.password = '12345testing'
        self.owner = User.objects.create_user(username='testowner', password=self.password)
        self.participant = User.objects.create_user(username='testparticipant1', password=self.password)
        self.admin = User.objects.create_user(username='testadmin1', password=self.password)
        self.outsider = User.objects.create_user(username='testoutsider', password=self.password)
        # Create shopping list
        self.shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.owner
        )
        # Add participants and admins to shopping list
        self.shopping_list.participants.add(self.participant)
        self.shopping_list.admins.add(self.admin)
        # Create items
        self.item_name = 'Sjokolade'
        self.item_amount = '1 stk'
        self.item = Item.objects.create(
            creator=self.owner,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )
        self.item_participant = Item.objects.create(
            creator=self.participant,
            name=self.item_name,
            amount=self.item_amount
        )
        self.item_admin = Item.objects.create(
            creator=self.admin,
            name=self.item_name,
            amount=self.item_amount,
            shopping_list=self.shopping_list
        )

    def test_delete_shopping_list(self):
        self.shopping_list.delete()
        bool_item_is_deleted = self.item not in Item.objects.all()
        bool_item_participant_is_deleted = self.item_admin not in Item.objects.all()
        bool_item_admin_is_deleted = self.item_participant not in Item.objects.all()
        bool_shopping_list_is_deleted = self.shopping_list not in ShoppingList.objects.all()
        self.assertTrue(bool_item_is_deleted)
        self.assertTrue(bool_item_participant_is_deleted)
        self.assertTrue(bool_item_admin_is_deleted)
        self.assertTrue(bool_shopping_list_is_deleted)

    def test_delete_item(self):
        self.item.delete()
        bool_item_is_deleted = self.item not in Item.objects.all()
        bool_shopping_list_is_deleted = self.shopping_list not in ShoppingList.objects.all()
        self.assertTrue(bool_item_is_deleted)
        self.assertFalse(bool_shopping_list_is_deleted)

    def test_get_user_shopping_lists(self):
        # Create shopping list where self.owner is participant
        shopping_list = ShoppingList.objects.create(
            title='en tittel',
            owner=self.participant
        )
        shopping_list.participants.add(self.owner)
        # Create shopping list where self.owner is admin
        shopping_list2 = ShoppingList.objects.create(
            title='en tittel',
            owner=self.participant
        )
        shopping_list2.admins.add(self.owner)

        owned_shopping_lists = ShoppingList.objects.filter(owner=self.owner)
        other_shopping_lists = ShoppingList.objects.filter(participants=self.owner)
        other2_shopping_lists = ShoppingList.objects.filter(admins=self.owner)
        my_shopping_lists = other_shopping_lists | owned_shopping_lists | other2_shopping_lists

        self.assertQuerysetEqual(my_shopping_lists.distinct().order_by('id'), ShoppingList.get_user_shopping_lists(self.owner), transform=lambda x: x)

    def test_user_is_member(self):
        self.assertTrue(self.shopping_list.user_is_member(self.owner))
        self.assertTrue(self.shopping_list.user_is_member(self.participant))
        self.assertTrue(self.shopping_list.user_is_member(self.admin))
        self.assertFalse(self.shopping_list.user_is_member(self.outsider))

    def test_user_has_admin_rights(self):
        self.assertTrue(self.shopping_list.user_has_admin_rights(self.owner))
        self.assertTrue(self.shopping_list.user_has_admin_rights(self.admin))
        self.assertFalse(self.shopping_list.user_has_admin_rights(self.outsider))
        self.assertFalse(self.shopping_list.user_has_admin_rights(self.participant))
