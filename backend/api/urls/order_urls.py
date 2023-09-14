from django.urls import path, include

from api.views.order_views import F14ViewSet, F14v2ViewSet
from api.routers.routers import OnlyListRouter
from backend.settings import API_PREFIX

orders_f14_report_router = OnlyListRouter()
orders_f14_report_router.register(r'orders_f14_report', F14ViewSet)

orders_f14v2_report_router = OnlyListRouter()
orders_f14v2_report_router.register(r'orders_f14v2_report', F14v2ViewSet)

urlpatterns = [
    path(API_PREFIX, include(orders_f14_report_router.urls)),
    path(API_PREFIX, include(orders_f14v2_report_router.urls)),
]
