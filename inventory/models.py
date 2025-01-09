from django.db import models
from decimal import Decimal


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
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="dispensed_medications"
    )
    medication = models.ForeignKey(
        Medication, on_delete=models.CASCADE, related_name="dispensed_medications"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Total cost for this medication
    date_dispensed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name} to {self.patient.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Automatically calculate total cost based on quantity and price
        self.cost = self.quantity * self.price
        super().save(*args, **kwargs)


class DispensedMedicationHistory(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="dispensed_histories"
    )
    medication_details = models.JSONField(default=list)  # Storing medication details as JSON
    procedure = models.CharField(
        max_length=255, blank=True, null=True
    )  # Procedure name (if any)
    procedure_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Procedure cost
    consultation_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Consultation charge
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Total cost, includes all charges
    date_dispensed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.patient.name} on {self.date_dispensed}"


    def save(self, *args, **kwargs):
        # Convert float costs in medication_details to Decimal and calculate the total cost
        total_medication_cost = sum(
            Decimal(str(item.get("cost", 0.00))) for item in self.medication_details
        )
        self.total_cost = (
            self.procedure_cost
            + self.consultation_charge
            + total_medication_cost
        )
        super().save(*args, **kwargs)

class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date_billed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billing for {self.patient.name} on {self.date_billed}"