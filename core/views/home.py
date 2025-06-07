from django.shortcuts import render

from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from ..models import TipoPago, Categoria, Ingreso, ConsumoFijoMensual, ConsumoDiario


def home(request):
    # Obtener fecha actual
    hoy = timezone.now().date()
    mes_actual = hoy.month
    año_actual = hoy.year
    
    # Obtener totales
    tipos_pago = TipoPago.objects.all()
    
    # Datos para resumen
    saldos = []
    total_ingresos = 0
    total_gastos_fijos = 0
    total_gastos_diarios = 0
    
    for tp in tipos_pago:
        # Calcular ingresos totales para este tipo de pago
        ingresos = Ingreso.objects.filter(tipo_pago=tp).aggregate(total=Sum('monto'))
        ingreso_total = ingresos['total'] or 0
        
        # Calcular gastos fijos para este tipo de pago
        gastos_fijos = ConsumoFijoMensual.objects.filter(
            tipo_pago=tp, 
            mes=mes_actual, 
            año=año_actual
        ).aggregate(total=Sum('monto'))
        gasto_fijo_total = gastos_fijos['total'] or 0
        
        # Calcular gastos diarios para este tipo de pago
        gastos_diarios = ConsumoDiario.objects.filter(
            tipo_pago=tp, 
            fecha__month=mes_actual, 
            fecha__year=año_actual,
            es_credito=False
        ).aggregate(total=Sum('monto'))
        gasto_diario_total = gastos_diarios['total'] or 0
        
        # Calcular saldo disponible
        saldo = ingreso_total - gasto_fijo_total - gasto_diario_total
        
        saldos.append({
            'tipo_pago': tp,
            'ingresos': ingreso_total,
            'gastos_fijos': gasto_fijo_total,
            'gastos_diarios': gasto_diario_total,
            'saldo': saldo
        })
        
        total_ingresos += ingreso_total
        total_gastos_fijos += gasto_fijo_total
        total_gastos_diarios += gasto_diario_total
    
    # Consumos fijos pendientes
    consumos_fijos_pendientes = ConsumoFijoMensual.objects.filter(
        mes=mes_actual, 
        año=año_actual,
        pagado=False
    ).order_by('tipo_pago')
    
    # Consumos recientes
    consumos_recientes = ConsumoDiario.objects.all().order_by('-fecha')[:10]
    
    context = {
        'saldos': saldos,
        'total_ingresos': total_ingresos,
        'total_gastos_fijos': total_gastos_fijos, 
        'total_gastos_diarios': total_gastos_diarios,
        'total_saldo': total_ingresos - total_gastos_fijos - total_gastos_diarios,
        'consumos_fijos_pendientes': consumos_fijos_pendientes,
        'consumos_recientes': consumos_recientes,
        'mes_actual': mes_actual,
        'año_actual': año_actual
    }
    
    return render(request, 'core/home.html', context)
