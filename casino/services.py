import abc
import random
from django.db import transaction
from .models import BaseWallet, Customer, Wallet
from .signals import deposit


class WalletService(object):
    """Service for operation on all user wallets"""
    def __init__(self, user):
        self.customer, _ = Customer.objects.get_or_create(user=user)
        self.euro_wallet = Wallet.objects.euro_wallet_get(self.customer)

    @transaction.atomic
    def create_bonus(self, bonus):
        if bonus.currency == Wallet.EURO:
            self.euro_wallet.amount += bonus.amount
            self.euro_wallet.save(update_fields=['amount'])
        else:
            wallet = Wallet(customer=self.customer)
            for field in BaseWallet._meta.fields:
                setattr(wallet, field.name, getattr(bonus, field.name))
            wallet.save()

    @transaction.atomic
    def bonus_to_euro(self, bonus_wallet):
        self.euro_wallet.amount += bonus_wallet.amount
        bonus_wallet.depleted = True
        bonus_wallet.amount = 0
        bonus_wallet.save(update_fields=['amount', 'depleted'])
        self.euro_wallet.save(update_fields=['amount'])

    @transaction.atomic
    def deposit(self, amount):
        self.euro_wallet.amount += amount
        self.euro_wallet.save(update_fields=['amount'])
        deposit.send(sender=self.__class__, wallet_service=self, amount=amount)

    @transaction.atomic
    def withdraw(self, amount):
        if self.euro_wallet.amount < amount:
            return False
        self.euro_wallet.amount -= amount
        self.euro_wallet.save(update_fields=['amount'])
        return True

    def ready_to_wage_all(self):
        return Wallet.objects.ready_to_wage_all(self.customer)

    def sorted_all(self):
        return Wallet.objects.sorted_all(self.customer)


class BaseGameService(metaclass=abc.ABCMeta):
    """Base class for future games"""
    def __init__(self, user):
        self.customer, _ = Customer.objects.get_or_create(user=user)

    @transaction.atomic
    def bet(self, amount):
        wallet = Wallet.objects.with_amount_first(self.customer, amount)
        if wallet is None:
            return 0, "Not enough money"

        amount_change, status = self.game_logic(amount)
        wallet.amount += amount_change
        wallet.save()
        self.customer.overall_spent_money += amount
        self.customer.save()

        return amount_change, status

    @abc.abstractmethod
    def game_logic(self, amount):
        pass


class SimpleGame(BaseGameService):
    """Game class example"""
    @staticmethod
    def _check_win():
        return bool(random.getrandbits(1))

    def game_logic(self, amount):
        if self._check_win():
            return amount, 'You won'
        else:
            return -amount, 'You lose'
