import uuid

from .models import Payment, Organization
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers


class WebhookSerializer(serializers.Serializer):
    operation_id = serializers.UUIDField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    payer_inn = serializers.CharField(max_length=12, min_length=10)
    document_number = serializers.CharField(max_length=50)
    document_date = serializers.DateTimeField()

    def validate_operation_id(self, value):
        if Payment.objects.filter(operation_id=value).exists():
            raise serializers.ValidationError("Платеж с таким operation_id уже существует")
        return value
    
    def validate_payer_inn(self, value):
        if not Organization.objects.filter(inn=value).exists():
            raise serializers.ValidationError("Организация с указанным ИНН не найдена")
        return value


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['inn', 'balance']
        read_only_fields = ['inn', 'balance']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['operation_id', 'amount', 'organization', 'document_number', 'document_date', 'created_at']
        read_only_fields = ['organization', 'created_at']
