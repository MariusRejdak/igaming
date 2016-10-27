from decimal import Decimal
from unittest.mock import Mock
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from nose_parameterized import parameterized

from .. import models, services


class WalletServiceCase(TestCase):
    fixtures = ['user.yaml']

    def setUp(self):
        self.user = User.objects.get()
        self.wallet_service = services.WalletService(self.user)

    def _get_euro_wallet(self):
        return models.Wallet.objects.euro_wallet_get(self.wallet_service.customer)

    def _assert_euro_amount(self, amount):
        self.assertEquals(self._get_euro_wallet().amount, amount)

    def test_create_customer(self):
        self.assertEquals(self.wallet_service.customer.user, self.user)

    def test_create_wallet(self):
        self.assertEquals(self.wallet_service.euro_wallet.customer.user, self.user)
        self.assertEquals(self.wallet_service.euro_wallet.currency, models.Wallet.EURO)

    def test_bonus(self):
        self.wallet_service.create_bonus(models.Bonus(
            amount=Decimal('10.00'),
            currency=models.Bonus.BONUS,
            wagering_requirement=1,
            action=models.Bonus.DEPOSIT,
            min_amount=0,
        ))
        wallet = models.Wallet.objects.last()
        self.assertEquals(wallet.amount, Decimal('10.00'))
        self.assertEquals(wallet.currency, models.Bonus.BONUS)
        self.assertEquals(wallet.wagering_requirement, 1)

        self.wallet_service.bonus_to_euro(wallet)
        euro_wallet = self._get_euro_wallet()
        self.assertEquals(euro_wallet.amount, Decimal('10.00'))
        self.assertTrue(wallet.depleted)

    def test_bonus_euro(self):
        euro_amount = self._get_euro_wallet().amount
        self.wallet_service.create_bonus(models.Bonus(
            amount=Decimal('10.00'),
            currency=models.Bonus.EURO,
            wagering_requirement=1,
            action=models.Bonus.DEPOSIT,
            min_amount=0,
        ))
        self._assert_euro_amount(euro_amount + Decimal('10.00'))

    def test_deposit(self):
        euro_amount = self._get_euro_wallet().amount
        self.wallet_service.deposit(Decimal('5'))
        self._assert_euro_amount(euro_amount + Decimal('5'))

    def test_withdraw(self):
        euro_amount = self._get_euro_wallet().amount
        self.assertFalse(self.wallet_service.withdraw(euro_amount + 1))
        self.assertTrue(self.wallet_service.withdraw(euro_amount))
        self._assert_euro_amount(0)


class BaseGameServiceCase(TestCase):
    fixtures = ['user.yaml', 'customer.yaml']

    class TestGameWin(services.BaseGameService):
        def game_logic(self, amount):
            return 1, 'win'

    class TestGameLose(services.BaseGameService):
        def game_logic(self, amount):
            return -1, 'lose'

    @staticmethod
    def _get_euro_wallet():
        return models.Wallet.objects.euro_wallet_get(models.Customer.objects.get())

    def setUp(self):
        self.user = User.objects.get()
        self.game_win = self.TestGameWin(self.user)
        self.game_lose = self.TestGameLose(self.user)

    @parameterized.expand([
        ('win', 0, 0),
        ('win', 10, 1),
        ('lose', 10, -1),
    ])
    def test_bet(self, name, money, expected_change):
        wallet = self._get_euro_wallet()
        wallet.amount = money
        wallet.save()
        game = getattr(self, "game_{}".format(name))

        amount_change, _ = game.bet(1)
        wallet = self._get_euro_wallet()
        self.assertEquals(amount_change, expected_change)
        self.assertEquals(wallet.amount, money + expected_change)


class SimpleGameServiceCase(SimpleTestCase):
    def setUp(self):
        services.SimpleGame.__init__ = Mock(return_value=None)
        self.game_win = services.SimpleGame(None)
        self.game_win._check_win = Mock(return_value=True)
        self.game_lose = services.SimpleGame(None)
        self.game_lose._check_win = Mock(return_value=False)

    def test_check_win(self):
        self.assertIsInstance(services.SimpleGame(None)._check_win(), bool)

    @parameterized.expand([
        ('win', 1, 1),
        ('lose', 1, -1),
    ])
    def test_game_logic(self, name, amount, expected):
        game = getattr(self, "game_{}".format(name))
        result, _ = game.game_logic(amount)
        self.assertEquals(result, expected)
