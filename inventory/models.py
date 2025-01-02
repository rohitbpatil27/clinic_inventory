from django.db import models
from django.contrib.auth.models import User

class Medication(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=255, default="Unknown")  # Add this field
    mr_number = models.CharField(max_length=255, default="Unknown")  # Add this field

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    contact = models.CharField(max_length=15, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)  # New field for diagnosis
    
    def __str__(self):
        return self.name

class DispensedMedication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_dispensed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name} to {self.patient.name} ({self.quantity})"
    
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.action} on {self.timestamp}"