from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .services import WalletService
from .models import Bonus, Customer, Wallet
from .signals import deposit


@receiver(user_logged_in)
def on_logged_in(sender, user, request, **kwargs):
    """Event user logged in"""
    wallet_service = WalletService(user)
    for bonus in Bonus.objects.for_action(Bonus.LOGIN, 0).all():
        wallet_service.create_bonus(bonus)


@receiver(deposit)
def on_deposit(sender, wallet_service, amount, **kwargs):
    """Event user deposited money"""
    for bonus in Bonus.objects.for_action(Bonus.DEPOSIT, amount).all():
        wallet_service.create_bonus(bonus)


@receiver(pre_save, sender=Wallet)
def on_wallet_update(sender, instance, **kwargs):
    """On wallet update checks if depleted"""
    if instance.is_bonus and instance.amount <= 0:
        instance.depleted = True


@receiver(post_save, sender=Customer)
def on_customer_update(sender, instance, **kwargs):
    """On customer update checks if any bonus wallet can be waged"""
    wallet_service = WalletService(instance.user)
    for wallet in wallet_service.ready_to_wage_all():
        wallet_service.bonus_to_euro(wallet)
