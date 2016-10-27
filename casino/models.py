from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models


class Customer(models.Model):
    """Additional data for user"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    overall_spent_money = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return self.user.get_username()


class BaseWallet(models.Model):
    EURO = 'EUR'
    BONUS = 'BNS'
    CURRENCY_CHOICES = (
        (EURO, 'Euro'),
        (BONUS, 'Bonus'),
    )

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    wagering_requirement = models.IntegerField()

    def clean(self):
        if self.is_bonus and (self.wagering_requirement < 1 or self.wagering_requirement > 100):
            raise ValidationError({'wagering_requirement': 'Bonus wallets require a wagering requirement between 1 and 100'})

    @property
    def is_bonus(self):
        return self.currency == self.BONUS

    class Meta:
        abstract = True


class WalletManager(models.Manager):
    def _bonus_wallets_qs(self, customer):
        return self.filter(customer=customer).exclude(currency=Wallet.EURO)

    def euro_wallet_get(self, customer):
        """Get single wallet with Euro"""
        return self.get_or_create(
            currency=Wallet.EURO,
            customer=customer,
            depleted=False,
            defaults={'amount': 0, 'wagering_requirement': 0},
        )[0]

    def with_amount_first(self, customer, amount):
        """Return first wallet containing amount"""
        euro_wallet = self.euro_wallet_get(customer)
        if euro_wallet.amount >= amount:
            return euro_wallet
        return self._bonus_wallets_qs(customer).filter(depleted=False, amount__gte=amount).order_by('created').first()

    def ready_to_wage_all(self, customer):
        """Return wallets qualified for wagering"""
        spent_money_q = customer.overall_spent_money - models.F('amount') * models.F('wagering_requirement')
        return self._bonus_wallets_qs(customer).filter(depleted=False, spent_money_on_start__lte=spent_money_q).all()

    def sorted_all(self, customer):
        """Get wallets, Euro is always first"""
        yield self.euro_wallet_get(customer)
        for wallet in self._bonus_wallets_qs(customer).order_by('created').all():
            yield wallet


class Wallet(BaseWallet):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    spent_money_on_start = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    depleted = models.BooleanField(default=False)

    objects = WalletManager()

    def clean_amount(self):
        if self.amount < 0:
            raise ValidationError({'amount': 'Cannot be negative'})

    def __str__(self):
        return "{}: {} {}".format(self.customer.user.get_username(), self.amount, self.currency)

    def save(self, *args, **kwargs):
        if not self.id:
            self.spent_money_on_start = self.customer.overall_spent_money
        return super().save(*args, **kwargs)


class BonusManager(models.Manager):
    def for_action(self, name, amount):
        return self.filter(action=name, min_amount__lte=amount)


class Bonus(BaseWallet):
    DEPOSIT = 'deposit'
    LOGIN = 'login'
    ACTION_CHOICES = (
        (DEPOSIT, 'Deposit'),
        (LOGIN, 'User login'),
    )

    action = models.CharField(max_length=7, choices=ACTION_CHOICES)
    min_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    objects = BonusManager()

    def clean_amount(self):
        if self.amount <= 0:
            raise ValidationError({'amount': 'Cannot be negative or equal 0'})

    def clean_min_amount(self):
        if self.min_amount < 0:
            raise ValidationError({'min_amount': 'Cannot be negative'})

    def __str__(self):
        return "{}: {} {}".format(self.action, self.amount, self.currency)

    class Meta:
        verbose_name_plural = 'bonuses'
