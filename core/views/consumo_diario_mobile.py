from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import ConsumoDiario, Categoria, TipoPago
from datetime import date, datetime


def consumo_diario_mobile(request):
    """Vista simplificada para el registro rápido de consumos diarios desde móviles"""
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            tipo_pago_id = request.POST.get('tipo_pago')
            categoria_id = request.POST.get('categoria')
            monto = request.POST.get('monto')
            fecha = request.POST.get('fecha') or timezone.now().date()
            descripcion = request.POST.get('descripcion', '')
            es_credito = request.POST.get('es_credito') == 'on'
            cuotas = request.POST.get('cuotas', 1)
            
            # Para crédito, podemos recibir el mes de la primera cuota
            mes_primera_cuota = request.POST.get('mes_primera_cuota')
            año_primera_cuota = request.POST.get('año_primera_cuota') or timezone.now().year
            
            if es_credito and mes_primera_cuota:
                fecha = date(int(año_primera_cuota), int(mes_primera_cuota), 1)
            else:
                fecha = request.POST.get('fecha') or timezone.now().date()
            
            # Validar y convertir datos
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            categoria = Categoria.objects.get(pk=categoria_id)
            monto = float(monto.replace(',', '.'))
            cuotas = int(cuotas) if cuotas else 1
            
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)
            
            # Validaciones
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('consumo_diario_mobile')
            
            if es_credito and tipo_pago.es_tarjeta_credito and cuotas <= 0:
                messages.error(request, 'El número de cuotas debe ser mayor a cero')
                return redirect('consumo_diario_mobile')
            
            # Crear el consumo
            consumo = ConsumoDiario(
                tipo_pago=tipo_pago,
                categoria=categoria,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
                es_credito=es_credito and tipo_pago.es_tarjeta_credito,
                cuotas=cuotas if es_credito and tipo_pago.es_tarjeta_credito else 1,
                pagado=True if not tipo_pago.es_tarjeta_credito else False
            )
            
            # Si es crédito y la fecha es distinta a "hoy", marcamos como que la primera cuota es después (si aplica)
            # Aunque en el móvil el usuario elige el MES directamente.
            # La lógica de modelos.py se encargará de generar cuotas a partir de self.fecha
            consumo.save()
            
            messages.success(request, 'Consumo registrado correctamente')
            return redirect('consumo_diario_mobile')  # Redirigir a la misma página para agregar otro
            
        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')
    
    import calendar
    hoy = timezone.now().date()
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    meses_restantes = []
    for m in range(hoy.month, 13):
        meses_restantes.append({
            'numero': m,
            'nombre': meses_es.get(m)
        })

    context = {
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'fecha_actual': hoy.isoformat(),
        'meses_restantes': meses_restantes,
        'año_actual': hoy.year
    }
    
    return render(request, 'core/consumo_diario/mobile_form.html', context)
