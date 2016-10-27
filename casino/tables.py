from django_tables2 import RequestConfig, Table
from .models import Wallet


class WalletTable(Table):
    class Meta:
        model = Wallet
        attrs = {'class': 'table table-striped'}

    @classmethod
    def prepare(cls, request, wallet_service):
        table = cls(wallet_service.sorted_all())
        RequestConfig(request).configure(table)
        return table
