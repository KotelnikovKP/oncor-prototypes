from django.urls import path, include

from api.routers.routers import FullRouter
from api.views.registry_views import DiagnosisRegistryViewSet
from backend.settings import API_PREFIX

diagnosis_registry_router = FullRouter()
diagnosis_registry_router.register(r'diagnosis_registry', DiagnosisRegistryViewSet, basename='diagnosis_registry')

urlpatterns = [
    path(API_PREFIX, include(diagnosis_registry_router.urls)),
]
