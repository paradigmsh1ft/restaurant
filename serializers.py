from rest_framework import serializers
from .models import MenuItem, Order, OrderItem, Invoice
from django.contrib.auth.models import User
from django.utils.timezone import now

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'menu_item_name', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'status', 'created_at', 'items']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'order', 'total_amount', 'paid', 'paid_at']
        read_only_fields = ['total_amount', 'paid_at']

    def create(self, validated_data):
        order = validated_data['order']
        total = sum([
            item.menu_item.price * item.quantity
            for item in order.items.all()
        ])
        invoice = Invoice.objects.create(order=order, total_amount=total, **validated_data)
        return invoice

    def update(self, instance, validated_data):
        if validated_data.get('paid') and not instance.paid:
            instance.paid = True
            instance.paid_at = now()
        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
