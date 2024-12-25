from django.contrib import admin
from .models import Patient, DispensedMedication

admin.site.register(Patient)
admin.site.register(DispensedMedication)

