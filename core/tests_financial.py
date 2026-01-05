from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from core.models import TipoPago, Categoria, Ingreso, ConsumoDiario, ConsumoFijoMensual

class FinancialEnhancementsTest(TestCase):
    def setUp(self):
        self.debit_card = TipoPago.objects.create(nombre="Debit", es_tarjeta_debito=True)
        self.credit_card = TipoPago.objects.create(nombre="Credit", es_tarjeta_credito=True)
        self.categoria = Categoria.objects.create(nombre="General")

    def test_debit_balance_calculation(self):
        # Initial balance 0
        self.assertEqual(self.debit_card.balance, 0)
        
        # Add income
        Ingreso.objects.create(tipo_pago=self.debit_card, monto=1000, fecha=timezone.now().date())
        self.assertEqual(self.debit_card.balance, 1000)
        
        # Add paid expense
        ConsumoDiario.objects.create(
            tipo_pago=self.debit_card, 
            categoria=self.categoria, 
            monto=200, 
            fecha=timezone.now().date(),
            pagado=True
        )
        self.assertEqual(self.debit_card.balance, 800)
        
        # Add paid fixed expense
        ConsumoFijoMensual.objects.create(
            tipo_pago=self.debit_card,
            categoria=self.categoria,
            monto=300,
            mes=timezone.now().month,
            año=timezone.now().year,
            pagado=True
        )
        self.assertEqual(self.debit_card.balance, 500)

    def test_credit_card_installments_timing(self):
        # Current month installments
        fecha_compra = date(2026, 1, 15)
        consumo_ahora = ConsumoDiario.objects.create(
            tipo_pago=self.credit_card,
            categoria=self.categoria,
            monto=3000,
            fecha=fecha_compra,
            es_credito=True,
            cuotas=3,
            primera_cuota_siguiente_mes=False
        )
        
        cuotas = ConsumoDiario.objects.filter(consumo_original=consumo_ahora).order_by('fecha')
        self.assertEqual(consumo_ahora.fecha, date(2026, 1, 15))
        self.assertEqual(cuotas[0].fecha, date(2026, 2, 15))
        self.assertEqual(cuotas[1].fecha, date(2026, 3, 15))

        # Next month installments
        consumo_despues = ConsumoDiario.objects.create(
            tipo_pago=self.credit_card,
            categoria=self.categoria,
            monto=3000,
            fecha=fecha_compra,
            es_credito=True,
            cuotas=3,
            primera_cuota_siguiente_mes=True
        )
        
        # The original object is modified in save() to be the first cuota
        # So we fetch it again to be sure
        consumo_despues.refresh_from_db()
        self.assertEqual(consumo_despues.fecha, date(2026, 2, 15))
        
        cuotas_despues = ConsumoDiario.objects.filter(consumo_original=consumo_despues).order_by('fecha')
        self.assertEqual(cuotas_despues[0].fecha, date(2026, 3, 15))
        self.assertEqual(cuotas_despues[1].fecha, date(2026, 4, 15))
