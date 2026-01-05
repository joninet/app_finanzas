from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from ..models import TipoPago


def tipo_pago_list(request):
    tipos_pago = TipoPago.objects.all().order_by('nombre')
    
    paginator = Paginator(tipos_pago, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Tipos de Pago'
    }
    
    return render(request, 'core/tipo_pago/list.html', context)


def tipo_pago_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        es_tarjeta_credito = request.POST.get('es_tarjeta_credito') == 'on'
        es_tarjeta_debito = request.POST.get('es_tarjeta_debito') == 'on'
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('tipo_pago_create')
        
        TipoPago.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            es_tarjeta_credito=es_tarjeta_credito,
            es_tarjeta_debito=es_tarjeta_debito
        )
        
        messages.success(request, 'Tipo de pago creado correctamente')
        return redirect('tipo_pago_list')
    
    context = {
        'titulo': 'Crear Tipo de Pago'
    }
    
    return render(request, 'core/tipo_pago/form.html', context)


def tipo_pago_update(request, pk):
    tipo_pago = get_object_or_404(TipoPago, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        es_tarjeta_credito = request.POST.get('es_tarjeta_credito') == 'on'
        es_tarjeta_debito = request.POST.get('es_tarjeta_debito') == 'on'
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('tipo_pago_update', pk=pk)
        
        tipo_pago.nombre = nombre
        tipo_pago.descripcion = descripcion
        tipo_pago.es_tarjeta_credito = es_tarjeta_credito
        tipo_pago.es_tarjeta_debito = es_tarjeta_debito
        tipo_pago.save()
        
        messages.success(request, 'Tipo de pago actualizado correctamente')
        return redirect('tipo_pago_list')
    
    context = {
        'tipo_pago': tipo_pago,
        'titulo': 'Editar Tipo de Pago'
    }
    
    return render(request, 'core/tipo_pago/form.html', context)


def tipo_pago_delete(request, pk):
    tipo_pago = get_object_or_404(TipoPago, pk=pk)
    
    if request.method == 'POST':
        try:
            tipo_pago.delete()
            messages.success(request, 'Tipo de pago eliminado correctamente')
        except Exception as e:
            messages.error(request, f'No se puede eliminar este tipo de pago porque está siendo utilizado: {str(e)}')
        
        return redirect('tipo_pago_list')
    
    context = {
        'tipo_pago': tipo_pago,
        'titulo': 'Eliminar Tipo de Pago'
    }
    
    return render(request, 'core/tipo_pago/delete.html', context)
