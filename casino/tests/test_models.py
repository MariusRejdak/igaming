from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from nose_parameterized import parameterized

from .. import models


class BaseWalletCase(SimpleTestCase):
    def test_euro_not_bonus(self):
        wallet = models.BaseWallet(
            amount=0,
            currency=models.BaseWallet.EURO,
            wagering_requirement=-1,
        )
        try:
            wallet.clean()
        except ValidationError:
            self.fail()
        self.assertFalse(wallet.is_bonus)

    @parameterized.expand([
        (1,),
        (5,),
        (100,),
    ])
    def test_bonus_valid(self, wagering_requirement):
        wallet = models.BaseWallet(
            amount=0,
            currency=models.BaseWallet.BONUS,
            wagering_requirement=wagering_requirement
        )
        try:
            wallet.clean()
        except ValidationError:
            self.fail()
        self.assertTrue(wallet.is_bonus)

    @parameterized.expand([
        (-1,),
        (0,),
        (101,),
    ])
    def test_bonus_invalid(self, wagering_requirement):
        wallet = models.BaseWallet(
            amount=0,
            currency=models.BaseWallet.BONUS,
            wagering_requirement=wagering_requirement
        )
        self.assertRaises(ValidationError, wallet.clean)
        self.assertTrue(wallet.is_bonus)


class WalletManagerEmptyCase(TestCase):
    fixtures = ['user.yaml', 'customer.yaml', 'wallets_empty.yaml']

    def setUp(self):
        self.customer = models.Customer.objects.get()
        self.wallets = models.Wallet.objects

    def _euro_wallets_count(self):
        return self.wallets.filter(currency=models.Wallet.EURO, customer=self.customer).count()

    def test_euro_wallet_get(self):
        wallet = self.wallets.euro_wallet_get(self.customer)
        self.assertIsInstance(wallet, models.Wallet)
        self.assertEquals(wallet.currency, models.Wallet.EURO)
        self.assertEquals(wallet.customer, self.customer)
        self.assertEquals(wallet.amount, 0)
        self.assertFalse(wallet.depleted)
        self.assertEquals(wallet, self.wallets.euro_wallet_get(self.customer))
        self.assertEquals(self._euro_wallets_count(), 1)

    def test_with_amount_first(self):
        self.assertIs(self.wallets.with_amount_first(self.customer, 10), None)

    def test_ready_to_wage_all(self):
        self.assertEquals(len(self.wallets.ready_to_wage_all(self.customer)), 0)

    def test_sorted_all(self):
        wallets = list(self.wallets.sorted_all(self.customer))
        self.assertEquals(wallets[0].currency, models.Wallet.EURO)
        self.assertEqual(wallets[1:], sorted(wallets[1:], key=lambda w: w.created))
        for w in wallets[1:]:
            self.assertTrue(w.is_bonus)


class WalletManagerCase(TestCase):
    fixtures = ['user.yaml', 'customer.yaml', 'wallets.yaml']

    def setUp(self):
        self.customer = models.Customer.objects.get()
        self.wallets = models.Wallet.objects

    def test_euro_wallet_get(self):
        wallet = self.wallets.euro_wallet_get(self.customer)
        self.assertEquals(wallet.amount, 5)

    def test_with_amount_first(self):
        self.assertIs(self.wallets.with_amount_first(self.customer, 20), None)

        euro_wallet = self.wallets.with_amount_first(self.customer, 5)
        self.assertEquals(euro_wallet.amount, 5)
        self.assertEquals(euro_wallet.currency, models.Wallet.EURO)

        bonus_wallet = self.wallets.with_amount_first(self.customer, 10)
        self.assertEquals(bonus_wallet.amount, 10)
        self.assertEquals(bonus_wallet.currency, models.Wallet.BONUS)

        bonus_wallet = self.wallets.with_amount_first(self.customer, 15)
        self.assertEquals(bonus_wallet.amount, 15)
        self.assertEquals(bonus_wallet.currency, models.Wallet.BONUS)

    def test_ready_to_wage_all(self):
        ready_to_wage = self.wallets.ready_to_wage_all(self.customer)
        self.assertEquals(len(ready_to_wage), 1)


class WalletCase(TestCase):
    fixtures = ['user.yaml', 'customer.yaml']

    def setUp(self):
        self.customer = models.Customer.objects.get()

    def test_valid(self):
        wallet = models.Wallet(
            customer=self.customer,
            amount=0,
            wagering_requirement=0
        )
        try:
            wallet.save()
        except ValidationError:
            self.fail()
        self.assertEquals(wallet.spent_money_on_start, Decimal('123.45'))

    def test_invalid(self):
        wallet = models.Wallet(
            customer=self.customer,
            amount=Decimal('-1'),
            wagering_requirement=0
        )
        self.assertRaises(ValidationError, wallet.clean_amount)


class BonusManagerCase(TestCase):
    fixtures = ['bonuses.yaml']

    def setUp(self):
        self.bonuses = models.Bonus.objects

    @parameterized.expand([
        ("deposit low", models.Bonus.DEPOSIT, 9, 0),
        ("deposit hith", models.Bonus.DEPOSIT, 10, 1),
        ("login", models.Bonus.LOGIN, 0, 1),
    ])
    def test_for_action(self, _, action, amount, count):
        self.assertEquals(self.bonuses.for_action(action, amount).count(), count)


class BonusCase(SimpleTestCase):
    def test_valid(self):
        bonus = models.Bonus(
            action=models.Bonus.DEPOSIT,
            min_amount=0,
            currency=models.Bonus.EURO,
            amount=1,
            wagering_requirement=0
        )
        try:
            bonus.clean_amount()
            bonus.clean_min_amount()
        except ValidationError:
            self.fail()

    def test_invalid(self):
        bonus = models.Bonus(
            action=models.Bonus.DEPOSIT,
            min_amount=-1,
            currency=models.Bonus.EURO,
            amount=0,
            wagering_requirement=0
        )
        self.assertRaises(ValidationError, bonus.clean_amount)
        self.assertRaises(ValidationError, bonus.clean_min_amount)
