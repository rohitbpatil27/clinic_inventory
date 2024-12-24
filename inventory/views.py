from django.shortcuts import render, redirect
from .models import Medication
from django.contrib import messages

def dashboard(request):
    return render(request, "index.html")

def add_medicine(request):
    if request.method == "POST":
        name = request.POST.get("name")
        quantity = int(request.POST.get("quantity"))
        Medication.objects.create(name=name, quantity=quantity)
        messages.success(request, "Medicine added successfully!")
        return redirect("dashboard")
    return render(request, "add_medicine.html")

def low_stock(request):
    medications = Medication.objects.filter(quantity__lt=10)
    return render(request, "low_stock.html", {"medications": medications})


def available_stock(request):
    medications = Medication.objects.filter(quantity__gt=0)  # Fetch medications with quantity > 0
    return render(request, "available_stock.html", {"medications": medications})

