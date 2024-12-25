from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Medication, Patient, DispensedMedication
from django.contrib import messages
from django.views.decorators.http import require_POST
from itertools import groupby

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use .get to avoid MultiValueDictKeyError
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

@login_required
def dashboard(request):
    return render(request, "index.html")

def add_medicine(request):
    if request.method == "POST":
        name = request.POST.get("name")
        quantity = int(request.POST.get("quantity"))
        expiry_date = request.POST.get("expiry_date")  # Capture expiry date from form

        # Save the medicine to the database
        Medication.objects.create(name=name, quantity=quantity, expiry_date=expiry_date)
        
        messages.success(request, "Medicine added successfully!")
        return redirect("add_medicine")  # Redirect to the same page to show success message

    return render(request, "add_medicine.html")

def low_stock(request):
    medications = Medication.objects.filter(quantity__lt=10)
    return render(request, "low_stock.html", {"medications": medications})


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

def medication_list(request):
    medications = Medication.objects.all()
    return render(request, 'medication_list.html', {'medications': medications})

def dispense_medication_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Validate action
        if not action:
            return JsonResponse({"status": "error", "message": "Action is required."})

        # Handle adding a new patient
        if action == "add_patient":
            name = request.POST.get("name")
            age = request.POST.get("age")
            contact = request.POST.get("contact", "")

            if not name or not age:
                return JsonResponse({"status": "error", "message": "Name and age are required."})

            try:
                patient = Patient.objects.create(name=name, age=age, contact=contact)
                return JsonResponse({
                    "status": "success",
                    "patient_id": patient.id,
                    "patient_name": patient.name
                })
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})

        # Handle dispensing medication
        elif action == "dispense_medication":
            try:
                patient_id = request.POST.get("patient_id")
                medication_id = request.POST.get("medication_id")
                quantity = int(request.POST.get("quantity"))

                if quantity <= 0:
                    return JsonResponse({"status": "error", "message": "Quantity must be a positive number."})

                medication = get_object_or_404(Medication, id=medication_id)
                patient = get_object_or_404(Patient, id=patient_id)

                if medication.quantity >= quantity:
                    # Update medication stock
                    medication.quantity -= quantity
                    medication.save()

                    # Record dispensed medication
                    DispensedMedication.objects.create(
                        patient=patient, medication=medication, quantity=quantity
                    )
                    return JsonResponse({"status": "success", "message": "Medication dispensed successfully."})
                else:
                    return JsonResponse({"status": "error", "message": "Not enough stock available."})
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid input for quantity."})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

        # Invalid action
        return JsonResponse({"status": "error", "message": "Invalid action."})

    # Render the form for dispensing medication
    medications = Medication.objects.all()
    patients = Patient.objects.all()
    return render(request, "dispense_medication.html", {"medications": medications, "patients": patients})