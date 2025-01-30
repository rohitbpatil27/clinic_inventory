import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinic_inventory.settings")
django.setup()

from inventory.dummy_data import create_dummy_data

create_dummy_data()
