from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Medication, Patient, DispensedMedication
from django.contrib import messages
from itertools import groupby
from django.http import JsonResponse

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use .get to avoid MultiValueDictKeyError
        password = request.POST.get('password')
        next_url = request.POST.get('next')  # Get the 'next' parameter from the POST request

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to 'next' URL if it exists, otherwise to the dashboard
            return redirect(next_url if next_url else 'dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    # Capture the 'next' parameter from the GET request and pass it to the template
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

@login_required
def dashboard(request):
    return render(request, "index.html")

@login_required
def add_medicine(request):
    if request.method == "POST":
        name = request.POST.get("name")
        company_name = request.POST.get("company_name")  # Capture company name from form
        quantity = int(request.POST.get("quantity"))
        expiry_date = request.POST.get("expiry_date")  # Capture expiry date from form

        # Save the medicine to the database
        Medication.objects.create(
            name=name,
            company_name=company_name,
            quantity=quantity,
            expiry_date=expiry_date
        )
        
        messages.success(request, "Medicine added successfully!")
        return redirect("add_medicine")  # Redirect to the same page to show success message

    return render(request, "add_medicine.html")

@login_required
def low_stock(request):
    medications = Medication.objects.filter(quantity__lt=10)
    return render(request, "low_stock.html", {"medications": medications})

@login_required
def available_stock(request):
    query = request.GET.get("search", "")  # Get the search query
    if query:
        medications = Medication.objects.filter(name__icontains=query, quantity__gt=0)
    else:
        medications = Medication.objects.filter(quantity__gt=0)

    # Group medications by company name
    grouped_medications = {}
    for company_name, meds in groupby(medications.order_by("company_name"), key=lambda x: x.company_name):
        grouped_medications[company_name] = list(meds)

    return render(
        request,
        "available_stock.html",
        {"grouped_medications": grouped_medications, "search_query": query},
    )

@login_required
def dispense_medication_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Validate action
        if not action:
            return JsonResponse({"status": "error", "message": "Action is required."})

        # Handle dispensing medication for multiple medications
        if action == "dispense_medication":
            try:
                patient_id = request.POST.get("patient_id")
                patient = get_object_or_404(Patient, id=patient_id)

                # Get list of medications and quantities from the form
                medications = request.POST.getlist("medications[]")
                quantities = request.POST.getlist("quantities[]")

                if len(medications) != len(quantities):
                    return JsonResponse({"status": "error", "message": "Mismatch between medications and quantities."})

                # Process each medication
                for medication_id, quantity_str in zip(medications, quantities):
                    try:
                        medication = get_object_or_404(Medication, id=medication_id)
                        quantity = int(quantity_str)

                        if quantity <= 0:
                            return JsonResponse({"status": "error", "message": "Quantity must be a positive number."})

                        if medication.quantity >= quantity:
                            # Update medication stock
                            medication.quantity -= quantity
                            medication.save()

                            # Record dispensed medication
                            DispensedMedication.objects.create(
                                patient=patient, medication=medication, quantity=quantity
                            )
                        else:
                            return JsonResponse({"status": "error", "message": f"Not enough stock for {medication.name}."})

                    except ValueError:
                        return JsonResponse({"status": "error", "message": "Invalid input for quantity."})
                    except Exception as e:
                        return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

                return JsonResponse({"status": "success", "message": "Medications dispensed successfully."})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

        # Invalid action
        return JsonResponse({"status": "error", "message": "Invalid action."})

    # Render the form for dispensing medication
    medications = Medication.objects.all()
    patients = Patient.objects.all()
    return render(request, "dispense_medication.html", {"medications": medications, "patients": patients})

# View for displaying patients and adding a new patient
def patient_details(request):
    search_query = request.GET.get('search', '')
    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(name__icontains=search_query)

    return render(request, 'patient_details.html', {'patients': patients})

# Adding a new patient
def add_patient(request):
    if request.method == "POST":
        name = request.POST.get("name")
        age = request.POST.get("age")
        contact = request.POST.get("contact", "")
        diagnosis = request.POST.get("diagnosis", "")  # Handle diagnosis field
        
        if name and age:
            patient = Patient.objects.create(name=name, age=age, contact=contact, diagnosis=diagnosis)
            messages.success(request, f"Patient {name} added successfully!")
            return redirect('patient_details')  # Use redirect to prevent resubmission
        else:
            messages.error(request, "Name and age are required.")
            return redirect('add_patient')
        
# Editing an existing patient
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        patient.name = request.POST.get("name")
        patient.age = request.POST.get("age")
        patient.contact = request.POST.get("contact", "")
        patient.diagnosis = request.POST.get("diagnosis", "")  # Handle diagnosis field
        patient.save()
        messages.success(request, f"Patient {patient.name} updated successfully.")
        return redirect('patient_details')
    return render(request, "patient_details.html", {"patient": patient})

# Deleting a patient
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    patient.delete()
    messages.success(request, "Patient deleted successfully.")
    return redirect('patient_details')
