from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from ..models import ConsumoFijoMensual, Categoria, TipoPago


def consumo_fijo_list(request):
    # Filtrar por mes y año
    fecha_filtro = request.GET.get('mes', None)
    pagado_filtro = request.GET.get('pagado', None)
    
    # Mes y año por defecto (actual)
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    
    # Procesar filtro de fecha si existe
    if fecha_filtro:
        try:
            fecha_partes = fecha_filtro.split('-')
            if len(fecha_partes) == 2:
                año_actual = int(fecha_partes[0])
                mes_actual = int(fecha_partes[1])
        except (ValueError, IndexError):
            pass
    
    # Filtrar por mes y año
    filtros = {
        'mes': mes_actual,
        'año': año_actual
    }
    
    # Aplicar filtro de pagado/pendiente si existe
    if pagado_filtro in ['0', '1']:
        filtros['pagado'] = (pagado_filtro == '1')
    
    # Obtener todos los consumos del mes filtrado (sin paginación)
    consumos_fijos = ConsumoFijoMensual.objects.filter(
        **filtros
    ).order_by('pagado', 'categoria')
    
    # Calcular totales
    total_consumos = sum(c.monto for c in consumos_fijos)
    total_pagado = sum(c.monto for c in consumos_fijos if c.pagado)
    total_pendiente = total_consumos - total_pagado
    
    # Obtener nombre del mes para mostrar
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    mes_nombre = meses_es.get(mes_actual, "Enero")
    
    # Generar lista de meses y años para el selector
    meses = [(i, meses_es.get(i)) for i in range(1, 13)]
    años = range(timezone.now().year - 2, timezone.now().year + 3)
    
    context = {
        'consumos_fijos': consumos_fijos,
        'titulo': 'Consumos Fijos Mensuales',
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'mes_nombre': mes_nombre,
        'meses': meses,
        'años': años,
        'total_consumos': total_consumos,
        'total_pagado': total_pagado,
        'total_pendiente': total_pendiente,
        'pagado': pagado_filtro
    }
    
    return render(request, 'core/consumo_fijo/list.html', context)


def consumo_fijo_create(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Obtener mes y año actuales
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    
    # Generar lista de meses y años para el selector
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    meses = [(i, meses_es.get(i)) for i in range(1, 13)]
    años = range(timezone.now().year - 1, timezone.now().year + 3)
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        categoria_id = request.POST.get('categoria')
        monto = request.POST.get('monto')
        mes = request.POST.get('mes')
        año = request.POST.get('año')
        descripcion = request.POST.get('descripcion')
        pagado = request.POST.get('pagado') == 'on'
        fecha_pago = request.POST.get('fecha_pago')
        
        try:
            tipo_pago = None
            if tipo_pago_id:
                tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            elif pagado:
                messages.error(request, 'Debe seleccionar un tipo de pago si el consumo está pagado')
                return redirect('consumo_fijo_create')

            categoria = Categoria.objects.get(pk=categoria_id)
            monto = float(monto.replace(',', '.'))
            mes = int(mes)
            año = int(año)
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('consumo_fijo_create')
            
            if not (1 <= mes <= 12):
                messages.error(request, 'El mes debe estar entre 1 y 12')
                return redirect('consumo_fijo_create')
            
            # Verificar si ya existe un consumo fijo para esta categoría en el mismo mes/año
            if ConsumoFijoMensual.objects.filter(categoria=categoria, mes=mes, año=año).exists():
                messages.error(request, 'Ya existe un consumo fijo para esta categoría en el mes y año seleccionados')
                return redirect('consumo_fijo_create')
            
            consumo_fijo = ConsumoFijoMensual(
                tipo_pago=tipo_pago,
                categoria=categoria,
                monto=monto,
                mes=mes,
                año=año,
                descripcion=descripcion,
                pagado=pagado
            )
            
            if pagado and fecha_pago:
                consumo_fijo.fecha_pago = fecha_pago
                
            consumo_fijo.save()
            
            messages.success(request, 'Consumo fijo registrado correctamente')
            return redirect('consumo_fijo_list')
            
        except (TipoPago.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'La categoría seleccionada no existe')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Registrar Consumo Fijo Mensual',
        'meses': meses,
        'años': años,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'fecha_actual': timezone.now().date().isoformat()
    }
    
    return render(request, 'core/consumo_fijo/form.html', context)


def consumo_fijo_update(request, pk):
    consumo_fijo = get_object_or_404(ConsumoFijoMensual, pk=pk)
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Generar lista de meses y años para el selector
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    meses = [(i, meses_es.get(i)) for i in range(1, 13)]
    
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    
    años = range(año_actual - 1, año_actual + 3)
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        categoria_id = request.POST.get('categoria')
        monto = request.POST.get('monto')
        mes = request.POST.get('mes')
        año = request.POST.get('año')
        descripcion = request.POST.get('descripcion')
        pagado = request.POST.get('pagado') == 'on'
        fecha_pago = request.POST.get('fecha_pago')
        
        try:
            tipo_pago = None
            if tipo_pago_id:
                tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            elif pagado:
                messages.error(request, 'Debe seleccionar un tipo de pago si el consumo está pagado')
                return redirect('consumo_fijo_update', pk=pk)

            categoria = Categoria.objects.get(pk=categoria_id)
            monto = float(monto.replace(',', '.'))
            mes = int(mes)
            año = int(año)
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('consumo_fijo_update', pk=pk)
            
            if not (1 <= mes <= 12):
                messages.error(request, 'El mes debe estar entre 1 y 12')
                return redirect('consumo_fijo_update', pk=pk)
            
            # Verificar si ya existe otro consumo fijo para esta categoría en el mismo mes/año
            if ConsumoFijoMensual.objects.filter(categoria=categoria, mes=mes, año=año).exclude(pk=pk).exists():
                messages.error(request, 'Ya existe un consumo fijo para esta categoría en el mes y año seleccionados')
                return redirect('consumo_fijo_update', pk=pk)
            
            consumo_fijo.tipo_pago = tipo_pago
            consumo_fijo.categoria = categoria
            consumo_fijo.monto = monto
            consumo_fijo.mes = mes
            consumo_fijo.año = año
            consumo_fijo.descripcion = descripcion
            consumo_fijo.pagado = pagado
            
            if pagado and fecha_pago:
                consumo_fijo.fecha_pago = fecha_pago
            elif not pagado:
                consumo_fijo.fecha_pago = None
                
            consumo_fijo.save()
            
            messages.success(request, 'Consumo fijo actualizado correctamente')
            return redirect('consumo_fijo_list')
            
        except (TipoPago.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, 'La categoría seleccionada no existe')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'consumo_fijo': consumo_fijo,
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Editar Consumo Fijo Mensual',
        'meses': meses,
        'años': años,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'fecha_pago': consumo_fijo.fecha_pago.isoformat() if consumo_fijo.fecha_pago else None
    }
    
    return render(request, 'core/consumo_fijo/form.html', context)


def consumo_fijo_delete(request, pk):
    consumo_fijo = get_object_or_404(ConsumoFijoMensual, pk=pk)
    
    if request.method == 'POST':
        consumo_fijo.delete()
        messages.success(request, 'Consumo fijo eliminado correctamente')
        return redirect('consumo_fijo_list')
    
    context = {
        'consumo_fijo': consumo_fijo,
        'titulo': 'Eliminar Consumo Fijo'
    }
    
    return render(request, 'core/consumo_fijo/delete.html', context)


def consumo_fijo_toggle(request, pk):
    """Marcar/desmarcar un consumo fijo como pagado."""
    consumo_fijo = get_object_or_404(ConsumoFijoMensual, pk=pk)
    
    # Si se intenta marcar como pagado, verificar que tenga tipo de pago
    if not consumo_fijo.pagado:
        if not consumo_fijo.tipo_pago:
            messages.error(request, 'No se puede marcar como pagado un consumo sin tipo de pago asignado. Por favor edite el consumo primero.')
            return redirect('consumo_fijo_list')
        
        # Verificar saldo si es tarjeta de débito
        if consumo_fijo.tipo_pago.es_tarjeta_debito:
            balance_actual = consumo_fijo.tipo_pago.balance
            if balance_actual < float(consumo_fijo.monto):
                messages.error(request, f'Saldo insuficiente en {consumo_fijo.tipo_pago.nombre}. Saldo actual: ${balance_actual:.2f}')
                return redirect('consumo_fijo_list')
        
    consumo_fijo.pagado = not consumo_fijo.pagado
    
    if consumo_fijo.pagado:
        consumo_fijo.fecha_pago = timezone.now().date()
    else:
        consumo_fijo.fecha_pago = None
        
    consumo_fijo.save()
    
    messages.success(request, 'Estado actualizado correctamente')
    return redirect(request.META.get('HTTP_REFERER', 'consumo_fijo_list'))
