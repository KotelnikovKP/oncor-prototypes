from django.urls import path, include

from api.routers.routers import FullRouter
from api.views.test_views import CompanyViewSet
from backend.settings import API_PREFIX

company_router = FullRouter()
company_router.register(r'company', CompanyViewSet, basename='company')

urlpatterns = [
    path(API_PREFIX, include(company_router.urls)),
]
