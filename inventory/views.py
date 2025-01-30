from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Medication, Patient, DispensedMedication, Billing, DispensedMedicationHistory
from django.contrib import messages
from itertools import groupby
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.db import transaction  # For atomicity
from decimal import Decimal
import logging
logger = logging.getLogger(__name__)

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
        action = request.POST.get("action")  # Determines if it's add/update or delete
        medicine_id = request.POST.get("medicine")  # Selected medicine ID
        name = request.POST.get("name")  # Medicine name
        company_name = request.POST.get("company_name")  # Company name
        quantity = request.POST.get("quantity")  # Quantity
        mr_number = request.POST.get("mr_number")  # MR number

        # Handle Delete Operation
        if action == "delete":
            if medicine_id and medicine_id != "new":
                try:
                    medication = Medication.objects.get(id=int(medicine_id))
                    medication.delete()
                    messages.success(request, f"Medicine '{medication.name}' deleted successfully!")
                except Medication.DoesNotExist:
                    messages.error(request, "Selected medicine does not exist.")
                except Exception as e:
                    messages.error(request, f"Error deleting medicine: {str(e)}")
            else:
                messages.error(request, "Please select a valid medicine to delete.")
            return redirect("add_medicine")

        # Validate quantity for add/update operations
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number greater than zero.")
            return redirect("add_medicine")

        # Handle "new" medicine creation
        if medicine_id == "new":
            try:
                Medication.objects.create(
                    name=name,
                    company_name=company_name,
                    quantity=quantity,
                    mr_number=mr_number,
                )
                messages.success(request, "New medicine added successfully!")
            except Exception as e:
                messages.error(request, f"Failed to add new medicine: {str(e)}")
            return redirect("add_medicine")

        # Handle updating existing medicine
        else:
            try:
                medication = Medication.objects.get(id=int(medicine_id))
                medication.quantity += quantity  # Update quantity
                medication.name = name  # Optionally update name
                medication.company_name = company_name  # Optionally update company name
                medication.mr_number = mr_number  # Optionally update MR number
                medication.save()

                messages.success(request, f"Stock for {medication.name} updated successfully!")
            except Medication.DoesNotExist:
                messages.error(request, "Selected medicine does not exist.")
            except Exception as e:
                messages.error(request, f"Failed to update medicine: {str(e)}")

        return redirect("add_medicine")

    # Render the form for adding, updating, or deleting medicine if GET request
    medicines = Medication.objects.all()
    return render(request, "add_medicine.html", {"medicines": medicines})

@login_required
def low_stock(request):
    medications = Medication.objects.filter(quantity__lt=10)
    return render(request, "low_stock.html", {"medications": medications})

@login_required
def available_stock(request):
    query = request.GET.get("search", "")  # Get the search query
    if query:
        medications = Medication.objects.filter(
            Q(name__icontains=query) | Q(company_name__icontains=query), 
            quantity__gt=0
        )
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
# View for displaying patients and adding a new patient
def patient_details(request):
    search_query = request.GET.get('search')
    if search_query:
        patients = Patient.objects.filter(
            Q(name__icontains=search_query) | 
            Q(contact__icontains=search_query) | 
            Q(diagnosis__icontains=search_query)
        )
    else:
        patients = Patient.objects.all()
    
    paginator = Paginator(patients, 10)  # Show 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'patient_details.html', {'page_obj': page_obj, 'search_query': search_query})

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
        
@login_required
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

@login_required
def dispense_medication_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if not action:
            return JsonResponse({"status": "error", "message": "Action is required."})

        if action == "dispense_medication":
            try:
                patient_id = request.POST.get("patient_id")
                if not patient_id:
                    return JsonResponse({"status": "error", "message": "Please select a patient."})

                patient = get_object_or_404(Patient, id=patient_id)
                medications = request.POST.getlist("medications[]")
                quantities = request.POST.getlist("quantities[]")
                prices = request.POST.getlist("prices[]")
                procedure = request.POST.get("procedure", "")
                procedure_cost = Decimal(request.POST.get("procedure_cost", 0.0))
                consultation_charge = Decimal(request.POST.get("consultation_charge", 0.0))

                if len(medications) != len(quantities) or len(medications) != len(prices):
                    return JsonResponse({"status": "error", "message": "Mismatch between medications, quantities, and prices."})

                if not (medications or procedure or consultation_charge):
                    return JsonResponse({"status": "error", "message": "Please add at least one medication or Procedure or Consultation."})

                total_medication_cost = 0
                medication_details = []

                # After processing all medications and calculating the total costs
                with transaction.atomic():
                    for medication_id, quantity_str, price_str in zip(medications, quantities, prices):
                        try:
                            medication = get_object_or_404(Medication, id=medication_id)
                            quantity = Decimal(quantity_str)
                            price_per_unit = Decimal(price_str)

                            if quantity <= 0 or price_per_unit < 0:
                                return JsonResponse({"status": "error", "message": "Quantity and price must be positive numbers."})

                            if medication.quantity >= quantity:
                                medication.quantity -= quantity
                                medication.save()

                                cost = quantity * price_per_unit
                                total_medication_cost += cost

                                medication_details.append({
                                    "name": medication.name,
                                    "quantity": float(quantity),
                                    "price": float(price_per_unit),
                                    "cost": float(cost)
                                })

                                DispensedMedication.objects.create(
                                    patient=patient,
                                    medication=medication,
                                    quantity=quantity,
                                    price=price_per_unit,
                                    cost=cost,
                                )
                            else:
                                return JsonResponse({"status": "error", "message": f"Not enough stock for {medication.name}."})

                        except ValueError:
                            return JsonResponse({"status": "error", "message": "Invalid input for quantity or price."})
                        except Exception as e:
                            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

                    # Total cost calculation
                    total_cost = total_medication_cost + procedure_cost + consultation_charge

                    DispensedMedicationHistory.objects.create(
                        patient=patient,
                        medication_details=medication_details,  # Directly pass the list of medication details
                        procedure=procedure,
                        cost=total_cost,  # Total of medications, procedure, and consultation
                        procedure_cost=procedure_cost,
                        consultation_charge=consultation_charge,
                    )


                    # Create Billing record
                    Billing.objects.create(
                        patient=patient,
                        total_amount=total_cost,
                        description="Dispense Medications"
                    )

                    return JsonResponse({"status": "success", "message": "Medications dispensed successfully.", "total_cost": total_cost})


            except Exception as e:
                return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

        # Invalid action
        return JsonResponse({"status": "error", "message": "Invalid action."})

    # Render the form for dispensing medication
    medications = Medication.objects.all()
    patients = Patient.objects.all()
    return render(request, "dispense_medication.html", {"medications": medications, "patients": patients})

@login_required
def dispensing_history_view(request):
    # Fetch the search query, from_date, and to_date from the request
    search_query = request.GET.get('search', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Fetch all records, prefetched with related patient data
    all_history = (
        DispensedMedicationHistory.objects.select_related('patient')
        .order_by('-date_dispensed')
    )

    # Apply search query filter
    if search_query:
        all_history = all_history.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__contact__icontains=search_query)  # Assuming 'contact' field exists
        )

    # Apply date range filter
    if from_date and to_date:
        try:
            all_history = all_history.filter(
                date_dispensed__date__range=[from_date, to_date]
            )
        except ValueError:
            # Log if there's a problem with date parsing
            logger.error(f"Invalid date range: {from_date} to {to_date}")

    # Initialize total sums
    total_medication_cost = 0
    total_procedure_cost = 0
    total_consultation_cost = 0
    total_cost = 0

    # Group records by patient and calculate totals
    grouped_history = {}
    for record in all_history:
        medication_cost = 0

        # Ensure medication_details is a list and calculate medication cost
        if isinstance(record.medication_details, list):
            medication_cost = sum(
                medication.get('cost', 0) for medication in record.medication_details
            )

        # Update totals
        total_medication_cost += medication_cost
        total_procedure_cost += record.procedure_cost or 0
        total_consultation_cost += record.consultation_charge or 0
        total_cost += record.cost or 0

        # Group records by patient
        if record.patient not in grouped_history:
            grouped_history[record.patient] = []
        grouped_history[record.patient].append(record)

    # Convert grouped dictionary to a list of tuples for pagination
    grouped_history_list = list(grouped_history.items())

    # Paginate the grouped history
    paginator = Paginator(grouped_history_list, 10)  # 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the response with the updated context
    return render(
        request,
        'dispensing_history.html',
        {
            'history': page_obj,
            'search_query': search_query,
            'total_medication_cost': total_medication_cost,
            'total_procedure_cost': total_procedure_cost,
            'total_consultation_cost': total_consultation_cost,
            'total_cost': total_cost,
            'from_date': from_date,
            'to_date': to_date,
        }
    )

