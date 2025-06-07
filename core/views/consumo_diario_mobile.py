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
            ConsumoDiario.objects.create(
                tipo_pago=tipo_pago,
                categoria=categoria,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
                es_credito=es_credito and tipo_pago.es_tarjeta_credito,
                cuotas=cuotas if es_credito and tipo_pago.es_tarjeta_credito else 1
            )
            
            messages.success(request, 'Consumo registrado correctamente')
            return redirect('consumo_diario_mobile')  # Redirigir a la misma página para agregar otro
            
        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')
    
    context = {
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'fecha_actual': timezone.now().date().isoformat()
    }
    
    return render(request, 'core/consumo_diario/mobile_form.html', context)
