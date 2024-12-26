from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('add_medicine/', views.add_medicine, name='add_medicine'),
    path('low_stock/', views.low_stock, name='low_stock'),
    path('available_stock/', views.available_stock, name='available_stock'),
    path('dispense_medication/', views.dispense_medication_view, name='dispense_medication_view'),
    path('patient_details/', views.patient_details, name='patient_details'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('edit_patient/<int:id>/', views.edit_patient, name='edit_patient'),
    path('delete_patient/<int:id>/', views.delete_patient, name='delete_patient'),
]
