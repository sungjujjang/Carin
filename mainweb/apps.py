from django.apps import AppConfig
import os


class MainwebConfig(AppConfig):
    name = 'mainweb'
    def ready(self):
        from . import scheduler
        scheduler.start()
