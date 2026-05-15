from django.apps import AppConfig
import sys

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        if 'runserver' in sys.argv:
          from . import updater
          updater.start()
    
