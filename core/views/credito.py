from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..models import Credito, TipoPago, Categoria, ConsumoFijoMensual

def credito_list(request):
    creditos = Credito.objects.all().order_by('-fecha_creacion')
    
    context = {
        'creditos': creditos,
        'titulo': 'Créditos y Préstamos'
    }
    
    return render(request, 'core/credito/list.html', context)

def credito_create(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        monto_cuota = request.POST.get('monto_cuota')
        cantidad_cuotas = request.POST.get('cantidad_cuotas')
        fecha_inicio = request.POST.get('fecha_inicio')
        categoria_id = request.POST.get('categoria')
        tipo_pago_id = request.POST.get('tipo_pago')
        
        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            tipo_pago = None
            if tipo_pago_id:
                tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            
            monto_cuota = float(monto_cuota.replace(',', '.'))
            cantidad_cuotas = int(cantidad_cuotas)
            
            if monto_cuota <= 0:
                messages.error(request, 'El monto de la cuota debe ser mayor a cero')
                return redirect('credito_create')
                
            if cantidad_cuotas < 1:
                messages.error(request, 'La cantidad de cuotas debe ser mayor a cero')
                return redirect('credito_create')
            
            Credito.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                monto_cuota=monto_cuota,
                cantidad_cuotas=cantidad_cuotas,
                fecha_inicio=fecha_inicio,
                categoria=categoria,
                tipo_pago=tipo_pago
            )
            
            messages.success(request, 'Crédito registrado correctamente. Se han generado las cuotas correspondientes.')
            return redirect('credito_list')
            
        except Categoria.DoesNotExist:
            messages.error(request, 'La categoría seleccionada no existe')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Nuevo Crédito',
        'fecha_actual': timezone.now().date().isoformat()
    }
    
    return render(request, 'core/credito/form.html', context)

def credito_delete(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    
    if request.method == 'POST':
        # Eliminar las cuotas generadas (ConsumoFijoMensual)
        # Nota: Django CASCADE ya debería hacer esto si configuramos related_name correctamente en la ForeignKey
        # Pero verificar si queremos eliminar SOLO las impagas o todas.
        # Por simplicidad, eliminamos todo si es CASCADE.
        credito.delete()
        messages.success(request, 'Crédito eliminado correctamente')
        return redirect('credito_list')
    
    # Check outstanding balance/paid installments for warning
    cuotas_totales = credito.cuotas_generadas.count()
    cuotas_pagadas = credito.cuotas_generadas.filter(pagado=True).count()
    
    context = {
        'credito': credito,
        'cuotas_totales': cuotas_totales,
        'cuotas_pagadas': cuotas_pagadas,
        'titulo': 'Eliminar Crédito'
    }
    
    return render(request, 'core/credito/delete.html', context)
