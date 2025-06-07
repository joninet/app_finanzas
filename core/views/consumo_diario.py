from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from django.utils import timezone
from ..models import ConsumoDiario, Categoria, TipoPago
from datetime import datetime


def consumo_diario_list(request):
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    categoria_id = request.GET.get('categoria')
    
    # Configurar filtro por defecto (mes actual si no hay filtros)
    if not fecha_desde and not fecha_hasta and not categoria_id:
        hoy = timezone.now().date()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1).date()
        fecha_desde = primer_dia_mes.isoformat()
    
    # Iniciar con todos los consumos
    consumos = ConsumoDiario.objects.all()
    
    # Aplicar filtros
    if fecha_desde:
        try:
            consumos = consumos.filter(fecha__gte=fecha_desde)
        except (ValueError, TypeError):
            messages.warning(request, 'Formato de fecha inválido para fecha desde')
    
    if fecha_hasta:
        try:
            consumos = consumos.filter(fecha__lte=fecha_hasta)
        except (ValueError, TypeError):
            messages.warning(request, 'Formato de fecha inválido para fecha hasta')
    
    if categoria_id and categoria_id.isdigit():
        consumos = consumos.filter(categoria_id=categoria_id)
    
    # Ordenar por fecha descendente (más reciente primero)
    consumos = consumos.order_by('-fecha')
    
    # Calcular totales
    total_consumos = sum(c.monto for c in consumos)
    total_efectivo = sum(c.monto for c in consumos if not c.tipo_pago.es_tarjeta_credito)
    total_credito = sum(c.monto for c in consumos if c.tipo_pago.es_tarjeta_credito)
    
    # Obtener categorías para el filtro
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Paginación
    paginator = Paginator(consumos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Consumos Diarios',
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'fecha_actual': timezone.now().date().isoformat(),
        'categorias': categorias,
        'categoria_id': categoria_id,
        'total_consumos': total_consumos,
        'total_efectivo': total_efectivo,
        'total_credito': total_credito
    }
    
    return render(request, 'core/consumo_diario/list.html', context)


def consumo_diario_create(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        categoria_id = request.POST.get('categoria')
        monto = request.POST.get('monto')
        fecha = request.POST.get('fecha') or timezone.now().date()
        descripcion = request.POST.get('descripcion')
        es_credito = request.POST.get('es_credito') == 'on'
        cuotas = request.POST.get('cuotas', 1)
        
        try:
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            categoria = Categoria.objects.get(pk=categoria_id)
            monto = float(monto.replace(',', '.'))
            cuotas = int(cuotas) if cuotas else 1
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('consumo_diario_create')
            
            if es_credito and tipo_pago.es_tarjeta_credito and cuotas <= 0:
                messages.error(request, 'El número de cuotas debe ser mayor a cero')
                return redirect('consumo_diario_create')
            
            ConsumoDiario.objects.create(
                tipo_pago=tipo_pago,
                categoria=categoria,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
                es_credito=es_credito and tipo_pago.es_tarjeta_credito,
                cuotas=cuotas if es_credito and tipo_pago.es_tarjeta_credito else 1
            )
            
            messages.success(request, 'Consumo diario registrado correctamente')
            return redirect('consumo_diario_list')
            
        except (TipoPago.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'El tipo de pago o categoría seleccionados no existen')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Registrar Consumo Diario',
        'fecha_actual': timezone.now().date().isoformat()
    }
    
    return render(request, 'core/consumo_diario/form.html', context)


def consumo_diario_update(request, pk):
    consumo_diario = get_object_or_404(ConsumoDiario, pk=pk)
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        categoria_id = request.POST.get('categoria')
        monto = request.POST.get('monto')
        fecha = request.POST.get('fecha') or timezone.now().date()
        descripcion = request.POST.get('descripcion')
        es_credito = request.POST.get('es_credito') == 'on'
        cuotas = request.POST.get('cuotas', 1)
        
        try:
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            categoria = Categoria.objects.get(pk=categoria_id)
            monto = float(monto.replace(',', '.'))
            cuotas = int(cuotas) if cuotas else 1
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('consumo_diario_update', pk=pk)
            
            if es_credito and tipo_pago.es_tarjeta_credito and cuotas <= 0:
                messages.error(request, 'El número de cuotas debe ser mayor a cero')
                return redirect('consumo_diario_update', pk=pk)
            
            # Cuidado: actualizar un consumo en cuotas puede afectar a los consumos fijos ya generados
            # Por simplicidad, si ya estaba en cuotas, no permitimos cambiar la cantidad
            if consumo_diario.es_credito and consumo_diario.cuotas > 1:
                messages.warning(request, 'No se puede modificar un consumo con cuotas ya registrado. Considere eliminarlo y crear uno nuevo.')
                return redirect('consumo_diario_list')
            
            consumo_diario.tipo_pago = tipo_pago
            consumo_diario.categoria = categoria
            consumo_diario.monto = monto
            consumo_diario.fecha = fecha
            consumo_diario.descripcion = descripcion
            consumo_diario.es_credito = es_credito and tipo_pago.es_tarjeta_credito
            consumo_diario.cuotas = cuotas if es_credito and tipo_pago.es_tarjeta_credito else 1
            consumo_diario.save()
            
            messages.success(request, 'Consumo diario actualizado correctamente')
            return redirect('consumo_diario_list')
            
        except (TipoPago.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'El tipo de pago o categoría seleccionados no existen')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'consumo_diario': consumo_diario,
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Editar Consumo Diario',
        'fecha_actual': consumo_diario.fecha.isoformat()
    }
    
    return render(request, 'core/consumo_diario/form.html', context)


def consumo_diario_delete(request, pk):
    consumo_diario = get_object_or_404(ConsumoDiario, pk=pk)
    
    # Advertencia: eliminar un consumo en cuotas no eliminará los consumos fijos mensuales ya generados
    
    if request.method == 'POST':
        consumo_diario.delete()
        messages.success(request, 'Consumo diario eliminado correctamente')
        return redirect('consumo_diario_list')
    
    context = {
        'consumo_diario': consumo_diario,
        'titulo': 'Eliminar Consumo Diario'
    }
    
    return render(request, 'core/consumo_diario/delete.html', context)
