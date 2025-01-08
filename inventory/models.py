from django.db import models

class Medication(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=255, default="Unknown")
    mr_number = models.CharField(max_length=255, default="Unknown")

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=255)
    age = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.CharField(max_length=15, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class DispensedMedication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    procedure = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Total cost for this medication
    date_dispensed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name} to {self.patient.name} ({self.quantity})"

class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date_billed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billing for {self.patient.name} on {self.date_billed}"