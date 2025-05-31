import logging
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from .permissions import IsAdminOrReadOnly, IsAdminOrInvoicePayOnly

from django.contrib.auth.models import User
from .models import MenuItem, Order, Invoice, OrderItem
from .serializers import UserSerializer, MenuItemSerializer, OrderSerializer, InvoiceSerializer, OrderItemSerializer

logger = logging.getLogger('restaurant')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        order.status = 'confirmed'
        order.save()
        logger.info(f"Замовлення #{order.id} підтверджено користувачем {request.user.username}")
        return Response({'status': 'confirmed'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def send_to_kitchen(self, request, pk=None):
        order = self.get_object()
        order.status = 'in_kitchen'
        order.save()
        return Response({'status': 'in_kitchen'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = 'completed'
        order.save()
        return Response({'status': 'completed'}, status=status.HTTP_200_OK)
    
    def perform_create(self, serializer):
        logger.info("Створюється нове замовлення клієнтом") 
        serializer.save()


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        if not invoice.paid:
            invoice.paid = True
            invoice.paid_at = now()
            invoice.save()
            invoice.order.status = 'paid'
            invoice.order.save()
            logger.info(f"рахунок #{invoice.id} оплачено користувачем {request.user.username}")  
            return Response({'status': 'paid'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Already paid'}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

