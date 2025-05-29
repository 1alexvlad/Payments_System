from django.urls import path
from .views import bank_webhook, organization_balance


app_name = 'api'


urlpatterns = [
    path('webhook/bank/', bank_webhook, name='bank-webhook'),
    path('organizations/<str:inn>/balance/', organization_balance, name='organization-balance'),

]
