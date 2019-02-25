from django import forms


class ItemForm(forms.Form):
    name = forms.CharField(
        max_length=80,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter name of item'
            }
        )
    )
    amount = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter amount of item'
            }
        )
    )


class ShoppingListForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter title of shopping list'
            }
        )
    )


class ShareForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter username'
            }
        )
    )
