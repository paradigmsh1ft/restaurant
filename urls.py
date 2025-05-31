from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, MenuItemViewSet, OrderViewSet, InvoiceViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)), 
]
