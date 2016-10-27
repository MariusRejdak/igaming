from django.dispatch import Signal

deposit = Signal(providing_args=['wallet_service', 'amount'])
"""Signal emitted after user deposits money on wallet"""
