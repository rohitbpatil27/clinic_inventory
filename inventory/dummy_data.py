from inventory.models import Medication, Patient, DispensedMedication, DispensedMedicationHistory, Billing
from decimal import Decimal
from datetime import datetime, timedelta
import random

def create_dummy_data():
    # Sample data for dermatology
    medication_names = [
        "Clobetasol Cream", "Salicylic Acid Ointment", "Retinoic Acid Gel",
        "Hydroquinone Cream", "Azelic Acid Cream", "Benzoyl Peroxide Gel",
        "Adapalene Gel", "Mupirocin Ointment", "Ketoconazole Cream", "Tacrolimus Ointment"
    ]
    procedures = [
        "Chemical Peel", "Laser Treatment", "Microdermabrasion",
        "Cryotherapy", "Electrocautery", "Phototherapy"
    ]
    consultation_charges = [200, 300, 400, 500, 600]

    # Create Medications
    medications = []
    for name in medication_names:
        medication = Medication.objects.create(
            name=name,
            quantity=random.randint(10, 100),
            company_name=f"Pharma Co {random.randint(1, 5)}",
            mr_number=f"MR-{random.randint(1000, 9999)}"
        )
        medications.append(medication)

    # Create Patients
    for i in range(10):
        patient = Patient.objects.create(
            name=f"Patient {i + 1}",
            age=random.randint(20, 60),
            contact=f"98765432{i + 10}",
            diagnosis=f"Diagnosis {i + 1}: Skin condition {random.randint(1, 5)}"
        )

        # Assign Medications and Dispensed History
        medication_count = random.randint(1, 3)  # Number of medications per patient
        selected_medications = random.sample(medications, medication_count)

        history = []
        total_history_cost = Decimal("0.00")
        for med in selected_medications:
            quantity_dispensed = random.randint(1, 10)
            price_per_unit = Decimal(random.uniform(20, 500)).quantize(Decimal("0.01"))
            total_cost = price_per_unit * Decimal(quantity_dispensed)

            # Add DispensedMedication
            DispensedMedication.objects.create(
                patient=patient,
                medication=med,
                quantity=quantity_dispensed,
                price=price_per_unit,
                cost=total_cost
            )

            # Add to history JSON
            history.append({
                "name": med.name,
                "quantity": str(quantity_dispensed),
                "cost": str(total_cost)
            })
            total_history_cost += total_cost

        # Add Procedure and History
        procedure_cost = Decimal(random.uniform(100, 2000)).quantize(Decimal("0.01"))
        consultation_charge = Decimal(random.choice(consultation_charges))
        total_cost = total_history_cost + procedure_cost + consultation_charge

        DispensedMedicationHistory.objects.create(
            patient=patient,
            medication_details=history,
            procedure=random.choice(procedures),
            procedure_cost=procedure_cost,
            consultation_charge=consultation_charge,
            cost=total_cost,
            date_dispensed=datetime.now() - timedelta(days=random.randint(0, 30))
        )

        # Add Billing
        Billing.objects.create(
            patient=patient,
            total_amount=total_cost,
            description=f"Billing for procedures and medications on {datetime.now().date()}",
            date_billed=datetime.now() - timedelta(days=random.randint(0, 30))
        )

    print("Dummy data created successfully.")
