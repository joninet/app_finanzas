from django.shortcuts import render
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from ..models import ConsumoFijoMensual, ConsumoDiario
import calendar
from datetime import date

def resumen_mensual(request):
    # Obtener mes y año de los parámetros GET o usar el actual
    hoy = timezone.now().date()
    # Formato esperado: YYYY-MM
    mes_param = request.GET.get('mes')
    
    if mes_param:
        try:
            año, mes = map(int, mes_param.split('-'))
        except ValueError:
            año, mes = hoy.year, hoy.month
    else:
        año, mes = hoy.year, hoy.month
        
    # Validar rangos
    if mes < 1 or mes > 12:
        mes = hoy.month
    
    # Nombre del mes
    mes_nombre = calendar.month_name[mes].capitalize()
    # En español (simple mapping)
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    mes_nombre = meses_es.get(mes, mes_nombre)
    
    # === 1. Consumos Fijos (incluye cuotas de Créditos) ===
    consumos_fijos = ConsumoFijoMensual.objects.filter(
        mes=mes,
        año=año
    ).select_related('categoria', 'tipo_pago', 'credito_origen').order_by('categoria__nombre')
    
    total_fijos = consumos_fijos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_fijos_pagado = consumos_fijos.filter(pagado=True).aggregate(Sum('monto'))['monto__sum'] or 0
    total_fijos_pendiente = total_fijos - total_fijos_pagado
    
    # === 2. Consumos con Tarjeta (Agrupados y Detalles) ===
    # Solo los consumos que son de crédito (cuotas o marcados como tal)
    consumos_tarjeta_all = ConsumoDiario.objects.filter(
        fecha__year=año,
        fecha__month=mes,
        es_credito=True
    ).select_related('tipo_pago', 'categoria').order_by('tipo_pago__nombre', 'fecha')

    # Agrupación para la tabla resumen: incluimos ID del tipo de pago y estado pagado
    tarjetas_resumen = consumos_tarjeta_all.values(
        'tipo_pago_id', 
        'tipo_pago__nombre'
    ).annotate(
        total=Sum('monto'),
        total_pagado=Sum('monto', filter=models.Q(pagado=True)),
        total_pendiente=Sum('monto', filter=models.Q(pagado=False))
    ).order_by('tipo_pago__nombre')
    
    # Asegurar que los campos no sean None
    for tarjeta in tarjetas_resumen:
        tarjeta['total_pagado'] = tarjeta['total_pagado'] or 0
        tarjeta['total_pendiente'] = tarjeta['total_pendiente'] or 0
    
    total_tarjetas = sum(item['total'] for item in tarjetas_resumen)
    total_tarjetas_pendiente = sum(item['total_pendiente'] for item in tarjetas_resumen)
    
    # === Totales Generales ===
    # El "Total del Mes" ahora es Fijos + Consumos de Tarjeta
    total_general = total_fijos + total_tarjetas
    total_general_pendiente = total_fijos_pendiente + total_tarjetas_pendiente
    
    context = {
        'titulo': f'Resumen de Pagos - {mes_nombre} {año}',
        'mes_actual': mes,
        'año_actual': año,
        'mes_filtro_value': f"{año}-{mes:02d}",
        'mes_nombre': mes_nombre,
        
        'consumos_fijos': consumos_fijos,
        'total_fijos': total_fijos,
        'total_fijos_pagado': total_fijos_pagado,
        'total_fijos_pendiente': total_fijos_pendiente,
        
        'tarjetas_resumen': tarjetas_resumen,
        'consumos_tarjeta_all': consumos_tarjeta_all, # Para los detalles en el modal
        'total_tarjetas': total_tarjetas,
        'total_tarjetas_pendiente': total_tarjetas_pendiente,
        
        'total_general': total_general,
        'total_general_pendiente': total_general_pendiente,
    }
    
    return render(request, 'core/resumen/dashboard.html', context)
