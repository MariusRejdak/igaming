from django import forms
from django.forms.widgets import RadioSelect


class BetForm(forms.Form):
    """Placing a bet"""
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=1)


class TransactionForm(forms.Form):
    """Depositing/withdrawing money from main wallet"""
    DEPOSIT = 'D'
    WITHDRAW = 'W'
    TRANSACTION_DIRECTION = (
        (DEPOSIT, 'Deposit'),
        (WITHDRAW, 'Withdraw'),
    )

    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    direction = forms.ChoiceField(
        choices=TRANSACTION_DIRECTION,
        widget=RadioSelect,
    )
