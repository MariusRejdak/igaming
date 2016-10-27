from django.apps import AppConfig


class CasinoConfig(AppConfig):
    name = 'casino'
    verbose_name = 'Casino'

    def ready(self):
        import casino.signal_handlers  # noqa: F401
