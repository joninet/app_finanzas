from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from ..models import ConsumoFijoMensual, Categoria, TipoPago


def consumo_fijo_list(request):
    # Filtramos por mes y año si se proporciona en la URL
    mes = request.GET.get('mes', timezone.now().month)
    año = request.GET.get('año', timezone.now().year)
    
    try:
        mes = int(mes)
        año = int(año)
    except ValueError:
        mes = timezone.now().month
        año = timezone.now().year
    
    consumos_fijos = ConsumoFijoMensual.objects.filter(
        mes=mes, 
        año=año
    ).order_by('pagado', 'categoria')
    
    paginator = Paginator(consumos_fijos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Generar lista de meses y años para el selector
    meses = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    años = range(timezone.now().year - 2, timezone.now().year + 3)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Consumos Fijos Mensuales',
        'mes_actual': mes,
        'año_actual': año,
        'meses': meses,
        'años': años
    }
    
    return render(request, 'core/consumo_fijo/list.html', context)


def consumo_fijo_create(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Obtener mes y año actuales
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    
    # Generar lista de meses y años para el selector
    meses = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
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
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
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
            messages.error(request, 'El tipo de pago o categoría seleccionados no existen')
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
    meses = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
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
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
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
            messages.error(request, 'El tipo de pago o categoría seleccionados no existen')
        except ValueError:
            messages.error(request, 'Valores numéricos inválidos')
    
    context = {
        'consumo_fijo': consumo_fijo,
        'tipos_pago': tipos_pago,
        'categorias': categorias,
        'titulo': 'Editar Consumo Fijo Mensual',
        'meses': meses,
        'años': años,
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
    consumo_fijo.pagado = not consumo_fijo.pagado
    
    if consumo_fijo.pagado:
        consumo_fijo.fecha_pago = timezone.now().date()
    else:
        consumo_fijo.fecha_pago = None
        
    consumo_fijo.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'consumo_fijo_list'))
