from django.urls import path, include

from api.views.patient_views import PatientViewSet
from api.routers.routers import ListRetrieveRouter
from backend.settings import API_PREFIX

patient_router = ListRetrieveRouter()
patient_router.register(r'patient', PatientViewSet)

urlpatterns = [
    path(API_PREFIX, include(patient_router.urls)),
]
