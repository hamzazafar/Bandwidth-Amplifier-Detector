from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # loading signals
        import core.signals
