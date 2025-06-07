from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from ..models import Ingreso, TipoPago


def ingreso_list(request):
    ingresos = Ingreso.objects.all().order_by('-fecha')
    
    paginator = Paginator(ingresos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Ingresos'
    }
    
    return render(request, 'core/ingreso/list.html', context)


def ingreso_create(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    fecha_actual = timezone.now().date()
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        monto = request.POST.get('monto')
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        
        try:
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            monto = float(monto.replace(',', '.'))
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('ingreso_create')
            
            Ingreso.objects.create(
                tipo_pago=tipo_pago,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion
            )
            
            messages.success(request, 'Ingreso registrado correctamente')
            return redirect('ingreso_list')
            
        except TipoPago.DoesNotExist:
            messages.error(request, 'El tipo de pago seleccionado no existe')
        except ValueError:
            messages.error(request, 'El monto debe ser un número válido')
    
    context = {
        'tipos_pago': tipos_pago,
        'titulo': 'Registrar Ingreso',
        'fecha_actual': fecha_actual.isoformat()
    }
    
    return render(request, 'core/ingreso/form.html', context)


def ingreso_update(request, pk):
    ingreso = get_object_or_404(Ingreso, pk=pk)
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    fecha_actual = timezone.now().date()
    
    if request.method == 'POST':
        tipo_pago_id = request.POST.get('tipo_pago')
        monto = request.POST.get('monto')
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        
        try:
            tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
            monto = float(monto.replace(',', '.'))
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('ingreso_update', pk=ingreso.pk)
            
            ingreso.tipo_pago = tipo_pago
            ingreso.monto = monto
            ingreso.fecha = fecha
            ingreso.descripcion = descripcion
            ingreso.save()
            
            messages.success(request, 'Ingreso actualizado correctamente')
            return redirect('ingreso_list')
            
        except TipoPago.DoesNotExist:
            messages.error(request, 'El tipo de pago seleccionado no existe')
        except ValueError:
            messages.error(request, 'El monto debe ser un número válido')
    
    context = {
        'ingreso': ingreso,
        'tipos_pago': tipos_pago,
        'titulo': 'Editar Ingreso',
        'fecha_actual': fecha_actual.isoformat()
    }
    
    return render(request, 'core/ingreso/form.html', context)


def ingreso_delete(request, pk):
    ingreso = get_object_or_404(Ingreso, pk=pk)
    
    if request.method == 'POST':
        ingreso.delete()
        messages.success(request, 'Ingreso eliminado correctamente')
        return redirect('ingreso_list')
    
    context = {
        'ingreso': ingreso,
        'titulo': 'Eliminar Ingreso'
    }
    
    return render(request, 'core/ingreso/delete.html', context)
