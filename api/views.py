import logging
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Organization, Payment, BalanceLog
from .serializers import WebhookSerializer, BalanceSerializer


logger = logging.getLogger(__name__)

@api_view(['POST'])
@csrf_exempt  
def bank_webhook(request):

    serializer = WebhookSerializer(data=request.data)

    if not serializer.is_valid():
        logger.warning(f'Невалидный вебхук: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            organization = Organization.objects.get(inn=serializer.validated_data['payer_inn'])

            payment = Payment.objects.create(
                operation_id=serializer.validated_data['operation_id'],
                amount=serializer.validated_data['amount'],
                organization=organization,
                document_number=serializer.validated_data['document_number'],
                document_date=serializer.validated_data['document_date']
            )

            previous_balance = organization.balance
            Organization.objects.filter(pk=organization.pk).update(
                balance=F('balance') + serializer.validated_data['amount']
            )
            organization.refresh_from_db()

            BalanceLog.objects.create(
                organization=organization,
                amount=serializer.validated_data['amount'],
                previous_balance=previous_balance,
                new_balance=organization.balance,
                payment=payment
            )
            
            logger.info(f"Платеж {payment.operation_id} успешно обработан. Новый баланс: {organization.balance}")
            
        return Response({"status": "success"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {str(e)}")
        return Response(
            {"error": "Internal server error"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def organization_balance(request, inn):
   
    organization = get_object_or_404(Organization, inn=inn)
    serializer = BalanceSerializer(organization)
    return Response(serializer.data)