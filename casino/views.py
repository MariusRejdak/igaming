from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import BetForm, TransactionForm
from .services import WalletService, SimpleGame
from .tables import WalletTable


class WalletContextMixin:
    @property
    def wallet_service(self):
        try:
            return getattr(self, '_wallet_service')
        except AttributeError:
            self._wallet_service = WalletService(self.request.user)
            return self._wallet_service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = WalletTable.prepare(self.request, self.wallet_service)
        return context


class TableView(LoginRequiredMixin, WalletContextMixin, FormView):
    template_name = 'casino/table.html'
    success_url = reverse_lazy('table')
    form_class = BetForm

    def form_valid(self, form):
        game = SimpleGame(self.request.user)
        change, status = game.bet(form.cleaned_data['amount'])
        messages.add_message(self.request, messages.SUCCESS if change > 0 else messages.ERROR, status)
        return super().form_valid(form)


class BankView(LoginRequiredMixin, WalletContextMixin, FormView):
    template_name = 'casino/bank.html'
    success_url = reverse_lazy('bank')
    form_class = TransactionForm

    def form_valid(self, form):
        direction = form.cleaned_data['direction']
        amount = form.cleaned_data['amount']
        if direction == TransactionForm.WITHDRAW:
            if self.wallet_service.withdraw(amount):
                messages.add_message(self.request, messages.SUCCESS, "Withdrawn {} EUR from wallet".format(amount))
            else:
                messages.add_message(self.request, messages.ERROR, "You don't have {} EUR".format(amount))
        elif direction == TransactionForm.DEPOSIT:
            self.wallet_service.deposit(amount)
            messages.add_message(self.request, messages.SUCCESS, "Deposited {} EUR on wallet".format(amount))

        return super().form_valid(form)
