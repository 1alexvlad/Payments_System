from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Organization(models.Model):
    inn = models.CharField(("ИНН"), max_length=12, unique=True)
    balance = models.DecimalField(("Баланс"), max_digits=15, decimal_places=2, default=0, 
                                  validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return f"Организация ИНН {self.inn} (Баланс: {self.balance})"
    


class Payment(models.Model):
    operation_id = models.UUIDField(("UUID операции"), unique=True)
    amount = models.DecimalField(("Сумма платежа"), max_digits=15, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='payments', verbose_name='Организация')
    document_number = models.CharField(("Номер документа"), max_length=50)
    document_date = models.DateTimeField(verbose_name='Дата документа')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"Платеж {self.operation_id} на сумму {self.amount}"


class BalanceLog(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='balance_logs', verbose_name='Организация')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Изменение баланса')
    previous_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Баланс до изменения')
    new_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Новый баланс')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Связанный платеж')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лог баланса'
        verbose_name_plural = 'Логи баланса'
        ordering = ['-created_at']

    def __str__(self):
        return (f"Изменение баланса {self.organization.inn}: "
                f"{self.previous_balance} → {self.new_balance}")