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
from decimal import Decimal, InvalidOperation
from django.utils.dateparse import parse_date
from datetime import datetime
from django.utils.timezone import make_aware
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
        # Capture form data
        action = request.POST.get("action")  # Determines if it's add/update or delete
        medicine_id = request.POST.get("medicine")  # Selected medicine ID
        name = request.POST.get("name")  # Medicine name
        company_name = request.POST.get("company_name")  # Company name
        quantity = request.POST.get("quantity")  # Quantity as string
        mr_number = request.POST.get("mr_number")  # MR number
        price_str = request.POST.get("price")  # Price per unit (as string)
        expiry_date_str = request.POST.get("expiry_date")  # Expiry date (as string, expected in YYYY-MM-DD format)

        # Parse expiry date (if provided)
        expiry_date = parse_date(expiry_date_str) if expiry_date_str else None

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number greater than zero.")
            return redirect("add_medicine")

        # Validate and parse price
        try:
            price = Decimal(price_str.strip())
            if price < 0:
                raise ValueError("Price must be non-negative.")
        except Exception:
            messages.error(request, "Invalid price. Please enter a valid number.")
            return redirect("add_medicine")

        # Handle delete operation
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

        # Handle new medicine creation
        if medicine_id == "new":
            try:
                Medication.objects.create(
                    name=name,
                    company_name=company_name,
                    quantity=quantity,
                    mr_number=mr_number,
                    price=price,
                    expiry_date=expiry_date,
                )
                messages.success(request, "New medicine added successfully!")
            except Exception as e:
                messages.error(request, f"Failed to add new medicine: {str(e)}")
            return redirect("add_medicine")

        # Handle updating existing medicine
        else:
            try:
                medication = Medication.objects.get(id=int(medicine_id))
                medication.quantity += quantity  # Increase quantity
                medication.name = name  # Optionally update name
                medication.company_name = company_name  # Optionally update company name
                medication.mr_number = mr_number  # Optionally update MR number
                medication.price = price  # Update price per unit
                medication.expiry_date = expiry_date  # Update expiry date
                medication.save()
                messages.success(request, f"Stock for {medication.name} updated successfully!")
            except Medication.DoesNotExist:
                messages.error(request, "Selected medicine does not exist.")
            except Exception as e:
                messages.error(request, f"Failed to update medicine: {str(e)}")
            return redirect("add_medicine")

    # For GET request, pass all medicines to the template for updating purposes
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
                # Retrieve and validate patient
                patient_id = request.POST.get("patient_id")
                if not patient_id:
                    return JsonResponse({"status": "error", "message": "Please select a patient."})
                patient = get_object_or_404(Patient, id=patient_id)

                # Retrieve lists of medications, quantities, and prices
                medications = request.POST.getlist("medications[]")
                quantities = request.POST.getlist("quantities[]")
                prices = request.POST.getlist("prices[]")

                # Retrieve optional fields and convert to Decimal (defaulting to 0.0)
                procedure = request.POST.get("procedure", "")
                try:
                    procedure_cost = Decimal(request.POST.get("procedure_cost", "0.0").strip() or "0.0")
                    consultation_charge = Decimal(request.POST.get("consultation_charge", "0.0").strip() or "0.0")
                    cash_amount = Decimal(request.POST.get("cash_amount", "0.0").strip() or "0.0")
                    upi_amount = Decimal(request.POST.get("upi_amount", "0.0").strip() or "0.0")
                    # Retrieve manually entered grand total
                    grand_total = Decimal(request.POST.get("grand_total", "0.0").strip() or "0.0")
                except (InvalidOperation, ValueError):
                    return JsonResponse({"status": "error", "message": "Invalid cost values. Please enter valid numbers."})

                # Check that lists have matching lengths
                if len(medications) != len(quantities) or len(medications) != len(prices):
                    return JsonResponse({"status": "error", "message": "Mismatch between medications, quantities, and prices."})

                # Ensure at least one medication or one of procedure/consultation is provided
                if not (medications or procedure or consultation_charge):
                    return JsonResponse({"status": "error", "message": "Please add at least one medication or Procedure or Consultation."})

                total_medication_cost = Decimal(0)
                medication_details = []

                # Process each medication within an atomic transaction
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

                                cost = (quantity * price_per_unit).quantize(Decimal("0.01"))
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
                        except (InvalidOperation, ValueError):
                            return JsonResponse({"status": "error", "message": "Invalid input for quantity or price."})
                        except Exception as e:
                            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

                    # Use the manually entered grand_total as the final total cost, quantized to 2 decimal places
                    total_cost = grand_total.quantize(Decimal("0.01"))

                    # Create history record using the provided totals and partial payment details
                    DispensedMedicationHistory.objects.create(
                        patient=patient,
                        medication_details=medication_details,
                        procedure=procedure,
                        procedure_cost=procedure_cost.quantize(Decimal("0.01")),
                        consultation_charge=consultation_charge.quantize(Decimal("0.01")),
                        total_cost=total_cost,
                        cash_amount=cash_amount.quantize(Decimal("0.01")),
                        upi_amount=upi_amount.quantize(Decimal("0.01")),
                    )

                    # Create billing record
                    Billing.objects.create(
                        patient=patient,
                        total_amount=total_cost,
                        description="Dispense Medications"
                    )

                    return JsonResponse({
                        "status": "success",
                        "message": "Medications dispensed successfully.",
                        "total_cost": str(total_cost)
                    })

            except Exception as e:
                return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})
        return JsonResponse({"status": "error", "message": "Invalid action."})

    # For GET requests, render the form with available patients and medications
    medications = Medication.objects.all()
    patients = Patient.objects.all()
    return render(request, "dispense_medication.html", {"medications": medications, "patients": patients})


@login_required
def dispensing_history_view(request):
    # Check if the user wants to clear filters
    if 'clear_filters' in request.GET:
        return redirect('dispensing_history')  # Redirect to reset filters

    # Fetch filters from request
    search_query = request.GET.get('search', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    from_time = request.GET.get('from_time', '00:00')  # Default to midnight
    to_time = request.GET.get('to_time', '23:59')  # Default to end of day

    # Convert date and time to datetime objects
    try:
        if from_date:
            from_datetime = make_aware(datetime.strptime(f"{from_date} {from_time}", "%Y-%m-%d %H:%M"))
        if to_date:
            to_datetime = make_aware(datetime.strptime(f"{to_date} {to_time}", "%Y-%m-%d %H:%M"))
    except ValueError:
        logger.error(f"Invalid date/time input: {from_date} {from_time} - {to_date} {to_time}")
        from_datetime, to_datetime = None, None

    # Get all history records ordered by dispensed date
    all_history = DispensedMedicationHistory.objects.select_related('patient').order_by('-date_dispensed')

    # Apply search filter
    if search_query:
        all_history = all_history.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__contact__icontains=search_query)
        )

    # Apply datetime range filter
    if from_date and to_date:
        all_history = all_history.filter(date_dispensed__range=[from_datetime, to_datetime])

    # Calculate totals
    total_medication_cost = Decimal(0)
    total_procedure_cost = Decimal(0)
    total_consultation_cost = Decimal(0)
    total_cost = Decimal(0)

    grouped_history = {}
    for record in all_history:
        medication_cost = sum(Decimal(med.get('cost', 0)) for med in record.medication_details) if isinstance(record.medication_details, list) else Decimal(0)

        total_medication_cost += medication_cost
        total_procedure_cost += record.procedure_cost or Decimal(0)
        total_consultation_cost += record.consultation_charge or Decimal(0)
        total_cost += record.total_cost or Decimal(0)

        grouped_history.setdefault(record.patient, []).append(record)

    # Aggregate total cash and UPI amounts
    total_cash = all_history.aggregate(total=Sum("cash_amount"))["total"] or Decimal("0.00")
    total_upi = all_history.aggregate(total=Sum("upi_amount"))["total"] or Decimal("0.00")

    # Paginate results
    grouped_history_list = list(grouped_history.items())
    paginator = Paginator(grouped_history_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'history': page_obj,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
        'from_time': from_time,
        'to_time': to_time,
        'total_medication_cost': total_medication_cost,
        'total_procedure_cost': total_procedure_cost,
        'total_consultation_cost': total_consultation_cost,
        'total_cost': total_cost,
        'total_cash': total_cash,
        'total_upi': total_upi,
    }
    return render(request, 'dispensing_history.html', context)
