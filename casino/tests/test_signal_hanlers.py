from unittest.mock import MagicMock, Mock, patch
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.test import SimpleTestCase, TestCase
from nose_parameterized import parameterized

from .. import models, services
from .. import signals


class SignalHandlersCase(TestCase):
    fixtures = ['user.yaml']

    @staticmethod
    def _on_logged_in(return_value):
        queryset = MagicMock(spec=models.Bonus.objects)
        with patch.object(models.BonusManager, 'for_action', return_value=queryset) as for_action:
            queryset.all.return_value = return_value
            user_logged_in.send(None, user=User.objects.get(), request=None)
        for_action.assert_called_with(models.Bonus.LOGIN, 0)

    def _mock_create_bonus(self, value):
        with patch.object(services.WalletService, 'create_bonus', return_value=None) as create_bonus:
            self._on_logged_in(value)
        return create_bonus

    def test_on_logged_in(self):
        bonus = Mock()
        create_bonus = self._mock_create_bonus([bonus])
        create_bonus.assert_called_with(bonus)

    def test_on_logged_in_no_bonus(self):
        create_bonus = self._mock_create_bonus([])
        create_bonus.assert_not_called()


class SignalOnDepositCase(SimpleTestCase):
    fixtures = ['bonuses.yaml']

    @staticmethod
    def _on_deposit(wallet_service, return_value):
        queryset = MagicMock(spec=models.Bonus.objects)
        with patch.object(models.BonusManager, 'for_action', return_value=queryset) as for_action:
            queryset.all.return_value = return_value
            signals.deposit.send(None, wallet_service=wallet_service, amount=10)
        for_action.assert_called_with(models.Bonus.DEPOSIT, 10)

    def test_on_deposit(self):
        bonus = Mock()
        wallet_service = Mock()
        self._on_deposit(wallet_service, [bonus])
        wallet_service.create_bonus.assert_called_with(bonus)

    def test_on_deposit_no_bonus(self):
        wallet_service = Mock()
        self._on_deposit(wallet_service, [])
        wallet_service.create_bonus.assert_not_called()


class SignalOnConsumerUpdateCase(TestCase):
    fixtures = ['user.yaml']

    def setUp(self):
        self.instance = Mock()
        self.instance.user = User.objects.get()

    def _mock_bonus_to_euro(self, value):
        with patch.object(services.WalletService, 'ready_to_wage_all', return_value=value), \
                patch.object(services.WalletService, 'bonus_to_euro', return_value=None) as bonus_to_euro:
            post_save.send(models.Customer, instance=self.instance)
        return bonus_to_euro

    def test_on_consumer_update_empty(self):
        bonus_to_euro = self._mock_bonus_to_euro([])
        bonus_to_euro.assert_not_called()

    def test_on_consumer_update(self):
        bonus = Mock()
        bonus_to_euro = self._mock_bonus_to_euro([bonus])
        bonus_to_euro.assert_called_with(bonus)


class SignalOnWalletUpdateCase(SimpleTestCase):
    @parameterized.expand([
        (True, 0, False, True),
        (True, 1, False, False),
        (True, 1, True, True),
        (False, 0, False, False),
    ])
    def test_on_wallet_update(self, is_bonus, amount, depleted, expected_depleted):
        instance = Mock()
        instance.is_bonus = is_bonus
        instance.amount = amount
        instance.depleted = depleted

        pre_save.send(models.Wallet, instance=instance)
        self.assertEquals(instance.depleted, expected_depleted)
